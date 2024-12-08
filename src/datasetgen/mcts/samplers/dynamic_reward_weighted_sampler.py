import math
import random
import statistics
from typing import Optional

import psycopg2
import tenacity
from psycopg2.extras import DictCursor
from tenacity import retry_if_exception_type, wait_exponential

from datasetgen.mcts.db_client import DBClient
from datasetgen.mcts.program import Program
from datasetgen.mcts.samplers.db_sampler import DBSampler


class DynamicRewardWeightedSampler(DBSampler):
    """
    Dynamic Reward-Weighted Sampler, which samples parents based on their reward scores,
    adjusted by a dynamic scaling factor that changes over time to balance exploration and exploitation.

    The adaptive compression strength acts like a dynamic temperature parameter that automatically cycles
    between exploration (low compression) and exploitation (high compression) phases.
    """

    def __init__(self, db_client: DBClient, max_conversation_length=20):
        super().__init__(db_client)
        self.max_conversation_length = max_conversation_length
        self.db_client = db_client

    @tenacity.retry(retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.InterfaceError)),
                    wait=wait_exponential(multiplier=1, min=4, max=10))
    async def sample_parent(self, version=1, compression_strength: Optional[float] = None, adaptive_period: int = 100) \
            -> Optional[Program]:

            """
            Sample parent with adjusted reward scaling.

            Args:
                version: The version of programs to sample from
                compression_strength: Fixed compression strength between 0 and 1.
                                    If None, uses adaptive compression. Higher values mean more exploitation. Lower means more exploration.
                adaptive_period: Number of steps for a full sine wave cycle when using
                                adaptive compression.
            """
            max_assistant_length = (self.max_conversation_length * 2) + 1

            try:
                with self.db_client.get_connection() as conn:
                    with conn.cursor(cursor_factory=DictCursor) as cur:
                        # First get the current step count for adaptive compression
                        if compression_strength is None:
                            cur.execute(f"SELECT COUNT(*) as step_count FROM programs WHERE version = {version}")
                            step_count = cur.fetchone()['step_count']
                            # Calculate adaptive compression using sine wave
                            # sin goes from -1 to 1, so we transform to 0 to 1
                            compression_strength = (math.sin(2 * math.pi * step_count / adaptive_period) + 1) / 2

                        cur.execute("""
                                WITH recent AS (
                                    SELECT id, value, conversation_json
                                    FROM programs
                                    WHERE version = %s 
                                    AND value IS NOT NULL
                                    AND jsonb_array_length(conversation_json->'messages') < %s
                                    ORDER BY created_at DESC
                                    LIMIT 300
                                )
                                SELECT id, value 
                                FROM recent
                                """, (version, max_assistant_length))

                        results = cur.fetchall()
                        if not results:
                            return None

                        # Get statistics of the value distribution
                        values = [row['value'] for row in results]
                        mean_value = statistics.mean(values)
                        std_value = statistics.stdev(values) if len(values) > 1 else 1.0

                        # Apply reward transformation to handle power-law distribution
                        def transform_reward(value):
                            # Z-score normalization
                            z_score = (value - mean_value) / std_value if std_value > 0 else 0

                            # Compress extreme values using tanh with current compression strength
                            compressed = math.tanh(z_score * compression_strength)

                            # Scale back to positive values and add small epsilon
                            return (compressed + 1.0) / 2.0 + 1e-6

                        # Log current compression state
                        print(f"Using compression strength: {compression_strength:.3f} "
                              f"({'adaptive' if compression_strength is None else 'fixed'})")

                        # Calculate transformed weights
                        weights = [
                            (row['id'], transform_reward(row['value']))
                            for row in results
                        ]

                        # Normalize weights
                        total_weight = sum(w[1] for w in weights)
                        if total_weight == 0:
                            sampled_id = random.choice([w[0] for w in weights])
                        else:
                            normalized_weights = [(id, w / total_weight) for id, w in weights]
                            sampled_id = random.choices(
                                [id for id, _ in normalized_weights],
                                weights=[w for _, w in normalized_weights],
                                k=1
                            )[0]

                        # Fetch the selected program
                        cur.execute("""
                                SELECT * FROM programs WHERE id = %s
                                """, (sampled_id,))

                        row = cur.fetchone()
                        return Program.from_row(dict(row)) if row else None
            except Exception as e:
                print(f"Error sampling parent: {e}")
                raise e
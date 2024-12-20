This is an experiment to see whether using the Mermaid graph DSL can help improve composition of complex graphs.

The idea is to map the objective into a graph, and then use the graph to guide the composition of the code.

The objective `Create a copper smelting setup with a furnace and a chest`

Would become:

```mermaid
flowchart TD
    %% Mining Setup
    DRILL[Burner Mining Drill] --> BELT[Transport Belt]

    %% Smelting Line
    BELT -->|insert| FURNACE[Stone Furnace]

    %% Output Storage
    FURNACE[Stone Furnace] -->|insert| CHEST[Iron Chest]

    %% Resource Input Note
    %% The burner mining drill needs coal for fuel
    %% The burner inserter needs coal for fuel
    %% The stone furnace needs coal for fuel
```

Which would then be translated into the following code:

```

```
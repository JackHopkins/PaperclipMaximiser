from multiprocessing import Lock, Manager, RLock


class Vocabulary:

    def __init__(self):
        self.mutex = Lock()

        manager = Manager()

        self.vocabulary = manager.dict({
            "character": -2
        })
        self.i_vocabulary = manager.dict({
            -2: "character"
        })

    def _get_vocabulary(self):
        return self.vocabulary, self.i_vocabulary

    def _update_vocabulary(self, item):
        """
        Including a mutex to ensure that the vocabulary is managed in a threadsafe way.
        Otherwise, two processes may allocate different items to the same index.
        """
        try:
            with self.mutex:
                keys = self.vocabulary.keys()
                next_index = len(keys)
                if item not in keys:
                    self.vocabulary[item] = next_index
                    self.i_vocabulary[next_index] = item
                    #print(f"vocab: {item} = {next_index}")

            item = self.vocabulary[item]
        except Exception as e:
            print(e)
        return item
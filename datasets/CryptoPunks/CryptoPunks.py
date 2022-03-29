"""CryptoPunks Data Set"""

import datasets

_DATA_URL = "https://drive.google.com/file/d/1d01VQ1plsB8ZIO5VF0LKV2MxdNQjvoCW/view?usp=sharing"

class CryptoPunks(datasets.GeneratorBasedBuilder):
    """CryptoPunks Data Set"""

    BUILDER_CONFIGS = [
        datasets.BuilderConfig(
            name="plain_images",
            version=datasets.Version("1.0.0", ""),
            description="Plain image import of CryptoPunks Dataset",
        )
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "img": datasets.Array3D(shape=(24, 24, 3), dtype="uint8"),
                    "label": datasets.features.ClassLabel(
                        names=[
                            "airplane",
                            "automobile",
                            "bird",
                            "cat",
                            "deer",
                            "dog",
                            "frog",
                            "horse",
                            "ship",
                            "truck",
                        ]
                    ),
                }
            ),
            supervised_keys=("img", "label"),
            homepage="https://www.cs.toronto.edu/~kriz/cifar.html",
            citation=_CITATION,
        )    

    def _split_generators(self, dl_manager):
        archive = dl_manager.download(_DATA_URL)

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN, gen_kwargs={"files": dl_manager.iter_archive(archive), "split": "train"}
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST, gen_kwargs={"files": dl_manager.iter_archive(archive), "split": "test"}
            ),
        ]

    def _generate_examples(self, files, split):
        """This function returns the examples in the raw (text) form."""

        if split == "train":
            batches = ["data_batch_1", "data_batch_2", "data_batch_3", "data_batch_4", "data_batch_5"]

        if split == "test":
            batches = ["test_batch"]
        batches = [f"cifar-10-batches-py/{filename}" for filename in batches]

        for path, fo in files:

            if path in batches:
                dict = pickle.load(fo, encoding="bytes")

                labels = dict[b"labels"]
                images = dict[b"data"]

                for idx, _ in enumerate(images):

                    img_reshaped = np.transpose(np.reshape(images[idx], (3, 32, 32)), (1, 2, 0))

                    yield f"{path}_{idx}", {
                        "img": img_reshaped,
                        "label": labels[idx],
                    }
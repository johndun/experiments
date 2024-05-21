## Template

Complete the following steps one at a time. If you run into any problems, stop your work and I will assist you. Do not use the PROJECT_PATH environment variable in any python scripts.

Checkout working branch
  - Create and checkout the dev branch.

{{instructions}}

Merge changes to the main branch
- Stage and commit all changes
- Merge changes to the main branch


## CR1: Create tiny test datasets

Initial setup
  - Create the following directories at the top level of the project: test_data, scripts

Create the `scripts/initialize_test_image_data.py` script
  - Accepts a single command line argument `--dataset_name`
  - Initializes the dataset using `datasets.load_dataset`
  - Creates a tiny version of the dataset containing the 1st 8 samples per split.
    - To accomplish this, treat the dataset as a dictionary with keys for each split and use the `select` function.
    - Convert the dictionary of splits to a DatasetDict to use `save_to_disk` in the next step.
  - Saves the DatasetDict to `test_data/tiny_{dataset_name}`

Verify functionality
- Use the script to create `test_data/tiny_mnist`
- Verify that the tiny_mnist dataset can be loaded in ipython and has 8 records in each split

## CR2: Create tiny cifar20 dataset

Create `test_data/tiny_cifar10` dataset
- View the `scripts/initialize_test_image_data.py` script
- Run the script with dataset_name =cifar10
- Verify that the tiny_cifar10 dataset can be loaded in ipython

## CR3: Data loader function

Setup
- Create the `data` directory and the `data/__init__.py` file. 
- Create `data/get_dataset.py` file.

Implement `get_dataset` in `data/get_dataset.py`
- Single string input `dataset_name_or_path`
- Check to see if `dataset_name_or_path` is a local path, if so, load it locally using `datasets.load_from_disk`
- Otherwise, load the dataset from the hub with `datasets.load_dataset`
- Return the loaded dataset

Verify functionality
- In ipython, use `get_dataset` to load `test_data/tiny_mnist` and verify it contains 8 records per split
- In ipython, use `get_dataset` to load `mnist` and verify the number of records

## CR4: `get_dataset` unit tests

Setup
- Create the `tests` directory
- View the `get_datasets` function in `data/get_datasets.py`

Implement unit tests for `get_dataset` function
- Test that `test_data/tiny_mnist` can be locally loaded. 
- Test that `mnist` can be loaded from the hub
- Run the tests with `pytest`









## Prompt 4: Interactive exploration to figure out how to calculate the min and max pixel values of an image dataset

Complete the following steps one at a time. If you run into any problems, stop your work and I will assist you.

- Using ipython, initialize the tiny mnist dataset using `dataset.load_from_disk("test_data/test_mnist")`
- Use `torchvision.transforms.ToTensor` to transform the dataset to torch tensors 

## Prompt 4: Prepare to work on normalization function

Complete the following steps:

- Create and checkout the `dev` branch
- Create an `image_data` subdirectory
- Create an `__init__.py` file in `image_data`.

## Prompt 4.1: Dataset normalization function

Write a function called `prepare_image_dataset` in `image_data/prepare_image_dataset.py` which does the following:

- Inputs a huggingface image dataset with a "train" split.
- Applies the torchvision.transforms.ToTensor() transform to the dataset.
- Calculates the min and max pixel value over the "train" split.
- Logs the min and max pixel values.
- Normalizes the dataset so that the pixel values have range [-1, 1].
- Returns the rescaled dataset.

Next:
- Use `ipython` to verify the function can be applied to the `test_data/test_mnist` dataset

## Prompt 5: Test prepare_image_dataset

- Create a `tests` subdirectory in the project
- Take a look at the `prepare_image_dataset` function in `image_data/prepare_image_dataset.py`
- Create unit tests for the function that use the `test_cifar10` and `test_mnist` test datasets.
- Run the tests to ensure the function is properly implemented

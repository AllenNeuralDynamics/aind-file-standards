# Documention standard for data acquisition repositories

A data acquisition repo is a repository containing code that controls acquisition of data. This is the code running on the computers controlling some experimental platform. 

Examples include fiber photometry acquisition or various behavioral tasks.  

This is the codebase that an internal or external scientist would clone/install if they were trying to install software to run a given experiment on a new rig. This is also the repository an engineer would consult when building infrastructure to support the task (e.g. processing pipelines). In either case, it's critical that the readme contain some minimal information that explains what the repo is, how to install it, and how to use it.

# Minimum README contents

Every AIND repository that controls data acquisition **must** contain the following sections.

## REPO NAME

The top level of the README should contain the repo name, followed by a concise description of the experimental modality that the repo controls. This would ideally be a plain text description of the modality similar to what would be written in the methods section of a paper where the modality is used and should also include a schematic. Note that schematics can easily be added to markdown documents by editing the document directly on github and simply pasting an image from the clipboard. Github will automatically embed the image and provide a permanent link.

For example, for a behavioral task, this description should be 1-2 paragraphs long and should describe the task at a high enough level for a scientist who has not been exposed to the task to understand the general task flow. Links to white papers or published methods papers would be ideal to allow interested users to get more information.

## (Optional) External documentation site

If you use tools for automated documentation generation (e.g. Sphinx, ReadTheDocs, etc) that build docs in a webpage, you should link that here. Github also provides a location for a link to external documentation on the right sidebar, which should be used also, though that does not replace the need to link external documentation here.

## Hardware Instructions

All data acquisition systems require hardware, which should be fully documented. It is important to include that hardware documentation here or, ideally, link to another resource that contains sufficient descriptions of the hardware to allow a new user to build a new system.

## Installation

Include full instructions for installing the package. Ideally these should be simple (if they're not simple, it probably means that the repository isn't structured appropriately). 

For example, if your package is on the Python Package Index (PyPI), which is encouraged, you would specify that the package can be installed with:

```
pip install <package_name>
```

If your package is not on PyPI, you can encourage a local build with:

```
pip install -e .
```

It is important that packages contain requirements specifications files (`pyproject.toml` or `requirements.txt`) so that all necessary dependencies are installed when the package is built. It should be possible to build and use the package in a fresh environment (i.e. no dependencies should be assumed to have been installed in advance).

## Example Use

Provide examples of use of the package. This is helpful both to verify correct installation of the package and to provide users with a starting place for learning more. At bare minimum, the software commands for initiating data collection after successful installation should be provided. 

For example, you could provide instructions for initiating the data collection system at the command line after successful installation:

```
python <run_script.py> <required args like subject_id, etc>
```

## Data Format

Users must specify the data formats produced by the data acquisition system. This is critical for engineers who are interacting with your data acquisition software to know what is produced by it. For example, engineers working on data processing pipelines need to know what the inputs to that pipleline are, so good documentation of your data format is critical.

You should specify both the files being produced, including the folder heirarchy, as well as the format of each file. For example, you're producing tabular data in a CSV file, you should list all headers. If you're producing binary data, you should specify it's properties. Overall, the goal is to provide enough information for a downstream user to interact with the output data without having to explore the data themselves.

## Additional optional sections

More documentation is [almost] always helpful. Additional sections you might consider including are:

* Contributing - a section describing guidelines for logging issues, making pull requests, etc.
* Testing - a section describing how to run tests.
* Citing - a description of how you would like this work to be cited if external users make use of it.

If the README becomes very long with specific instructions for use, authors are encouraged to break the documentation into logical sections and store individual markdown files in a `docs` folder at the root of the repo, with links from the README. For example, if there are very specific instructions for how to interact with a graphical user interface, these likely belong in a separate document.
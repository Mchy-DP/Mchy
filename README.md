# Mchy
Mchy is a compiler which converts the custom language, *Mchy*, to *Minecraft Datapacks*.  This allows the programmer to write high level code such as for-loops, if-statements and functions yielding return values. They can then call the compiler and let it deal with the many idiosyncrasies of Datapacks that usually make these features difficult to implement and the code near impossible to read.

## Quick Links
* [Getting Started](#getting-started)
* [Documentation](/docs/home.md)

## Getting started
1. Download The Compiler
    - <details>
        <summary>Windows</summary>
        
        Download the `mchy.exe` file from the [latest release](https://github.com/Mchy-DP/Mchy/releases/latest).
    </details>

    - <details>
        <summary>Linix/Mac etc</summary>
        
        Other Operating systems are not officially supported but will probably work.  You will need to build the compiler yourself using the build script in [dev_util](/dev_util).  Note: you will need [Java](https://www.java.com/), [ANTLR (v4.10)](https://www.antlr.org/download/antlr-4.10-complete.jar) & [Python](https://www.python.org/downloads/) downloaded along with pip installing the [antlr4-python3-runtime](https://pypi.org/project/antlr4-python3-runtime/).  For the rest of this section I will assume `mchy.exe` is being used on windows, when this is seen other operating systems can use `python -m mchy` as one-to-one replacement assuming mchy is on the path.
    </details>

2. Get mchy on the path
    - <details>
        <summary>Quick and easy way</summary>
        
        Copy the downloaded `mchy.exe` file to the folder you want to write mchy code in.
    </details>

    - <details>
      <summary>Long and robust way</summary>
        
        Copy the downloaded `mchy.exe` file somewhere safe on your computer then add that directory to the windows `Path` variable.  Steps to add a folder to the path:
        1. Press the windows button/key
        2. Type `edit environment variables for your account` into the search bar
        3. Click the top result
        4. In the top box of the opened window entitled `User variables for USERNAME` find the `Path` variable
        5. Click the `Path` variable once to select it
        6. Press the `Edit` button directly below the top box
        7. Press the `New` button from the left hand menu
        8. Paste the path to the directory containing the `mchy.exe` file in the new entry.
    </details>

3. Create a hello world program
    - Create a new file called `hello_world.mchy`
    - Paste the following code into it
      ```py
      print("Hello world!")
      ```
    - Save the file

4. Open the directory containing the program in the terminal
    - **Shift** + **Right Click** in the directory containing the program and select `Open PowerShell window here`.  Note on older versions it may say `Open Command window here`, that is also fine.

5. Run the compiler
    - Type the following into the terminal:
      ```cmd
      mchy.exe -v .\hello_world.mchy
      ```
      Note: You may need to prefix the command with `.\` if you chose to put `mchy.exe` in the same folder during step 2.  This would make the full command:
      ```cmd
      .\mchy.exe -v .\hello_world.mchy
      ```
      If all goes well you should see the output `Compilation Successful!` after the compiler finishes.

6. Move your Datapack to your world
    - In the folder containing the program there should now be a folder called `Hello World`.  This folder is the Datapack.  It can now be moved to the `datapacks` folder of any Minecraft world and then when `/reload` is run in chat in that Minecraft world you should see the message `Hello World!` output to chat.

### Tips:
  - Getting bored of copying your Datapack over after making a change, get the compiler to build straight to the `datapacks` directory via the `-o` option.  Example:
    ```
    mchy.exe -v -o C:\Users\USERNAME\AppData\Roaming\.minecraft\saves\test_world\datapacks .\hello_world.mchy
    ```
  - Encountered a bug?  You need a log file!  Add the option `--log-file .\mchy.log` to generate a log file in the same directory.  Example:
    ```
    mchy.exe -v --log-file .\mchy.log .\hello_world.mchy
    ```
  - Want to know more about the language, check the documentation or examples.  Want to see what other options you can give the compiler try running `mchy.exe --help` to see other options.

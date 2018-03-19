=============
annual_report
=============

Annual Report Link Aggregator and Downloader.

The program scrapes the links to Annual Reports for NSE Symbols and
downloads them.


Quick Summary
-------------

If you want to follow all the sensible defaults, make sure there is a
file called ``download_symbols.txt`` alongside this file which contains
the NSE symbols you are interested in (see ``all_symbols.txt`` for
example), then run:

    python3 annual_report.py -a -d

To see all the available arguments, pass the ``-h`` or ``--help``
argument like:

    python3 annual_report.py -h
    annual_report.exe --help

If you are using annual_report.exe instead of the Python script, then
replace ``python3 annual_report.py`` with ``annual_report.exe`` in all
the commands you run. For example:

    python3 annual_report.py -a -d

becomes:

    annual_report.exe -a -d


Installation/Usage instructions
-------------------------------

Windows Users
+++++++++++++

You are suggested to use the ``annual_report.exe`` file to run all the
commands. Otherwise, follow the steps to install Python and required
third-party modules and use the ``annual_report.py`` Python script to
run the commands.

1. The program is written and tested in Python 3.4. Go to `Python
   Downloads page`__ to download the latest version of it.

   .. __: https://www.python.org/downloads/

2. Install it with all the default settings, but make sure to enable the
   option which says **Add python.exe to path**.

3. Next, install all the 3rd party modules required for this program.
   Start Powershell or Command Prompt (cmd), navigate to this program's
   directory (see `Tips for mostly Windows users`_ section below) and
   execute the following command:

       pip3 install -r requirements.txt

   In case, the command fails saying it couldn't recognize ``pip3``,
   execute the following and then re-run the above command.

       set PATH=%PATH%;C:\Python34\Scripts    # if using cmd
       $env:path += ";C:\Python34\Scripts"    # if using powershell

4. If everything went well, you should be able to run this program.
   Execute the following to see all the available arguments for this
   program:

       python annual_report.py -h

Mac/Linux Users
+++++++++++++++

1. Python is installed on most of the distributions. If not, install it
   using your package manager. Make sure to install and use Python 3.

2. Install all the third-party modules required for this program. You
   should have the ``pip3`` program installed. If it isn't already
   installed, use the package manager to install it as well. Once,
   ``pip3`` is available, navigate to this program's directory and
   execute the following command:

       pip3 install -r requirements.txt

3. If everything went well, you should be able to run this program.
   Execute the following to see all the available arguments for this
   program:

       python3 annual_report.py -h


Advanced Guidance
-----------------

There are two aspects with regard to this program:

 1. Link Aggregation: The program scrapes the links to Annual Reports
                      for every symbol mentioned in the Symbol File and
                      stores them in ``annual_report_links.json`` file
                      in the working directory.
 2. Report Download: When downloading, the above-mentioned JSON file is
                     used to get the link for a particular financial
                     year for every symbol mentioned in the Symbol File.

Before you begin downloading the reports, you need to aggregate the
links for the symbols you are interested in. Link aggregation would
fetch the latest links to Annual report and add it to the JSON file,
which would be used to download the reports.


How to use this program
+++++++++++++++++++++++

1. Create a file for NSE Symbols for which you are interested in
   downloading the Annual Reports. By default, the program looks for a
   file called ``download_symbols.txt`` in the working directory;
   otherwise pass the location to the file as argument to ``-s`` or
   ``--symbol-file``. Put the Symbols separated by newlines in this
   file.

2. Then, run the program to aggregate all the links in the JSON file.

       python3 annual_report.py -a    # when you use "download_symbols.txt"
       python3 annual_report.py -a -s "/path/to/file"

3. Once, you have the links aggregated, you may download the Annual
   Reports for each financial year.

       # Following commands would download the reports for the latest
       # financial year
       python3 annual_report.py -d    # when you use "download_symbols.txt"
       python3 annual_report.py -d -s "/path/to/file"

       # To download the reports for another financial year (2011-2012):
       python3 annual_report.py -d -fy "2011-2012"
       python3 annual_report.py -d -fy "2011-2012" -s "/path/to/file"

   The program downloads the reports in working directory by default,
   separated by different folders for each financial year. To download
   the reports in another base directory, pass the location as an
   argument to ``--base-download-folder``, like:

       python3 annual_report.py -d --base-download-folder "/path/to/folder"

   (If there already exists a file with similar name, the file isn't
   downloaded.)

4. Financial year: A couple of companies follow calendar year as their
                   financial year. The program treats them differently.
                   If calendar-year-cum-financial-year is 2013, the
                   financial year is considered as 2013-2014.

5. Latest financial year: If the current year is 2014, the report by
                          default, would be downloaded for financial
                          year 2013-2014, as the latest financial year.

6. If you are using a binary version of this program (like *.exe file),
   replace ``python3 annual_report.py`` in all the above commands with
   ``annual_report.exe``.

7. See the optional arguments available for other advanced options.


Tips for mostly Windows users
-----------------------------

1. I recommend to use Windows Powershell instead of Command Prompt.
   Press Win + R and type ``powershell`` to start it. If this file is
   stored in ``D:\Markets\AnnualReport`` folder, run the following
   command to change directory (``cd``) to that folder:

       cd "D:\Markets\AnnualReport"

2. See `this Technet article`__ to make your life much healthier with
   regard to console appearance:

   .. __: http://technet.microsoft.com/en-in/library/ee156814.aspx

   Personal preferences:

    * Font: Consolas; Size: 20
    * Colors: ScreenText (192, 192, 192); ScreenBackground (0, 0, 0)
    * Layout: ScreenBufferSize (120, 9999); WindowSize (120; 25)

3. Most of the long-form arguments work even if they are incomplete and
   there isn't any ambiguity as to what you want, like:

    * ``--base`` should also work instead of ``--base-download-folder``
    * ``--rename`` should also work instead of ``--rename-existing``

4. Learn to use the Tab key to auto-complete commands and file/folder
   names. As well as the up-and-down arrow keys for earlier history.

5. In order to stop the program when it is running, prefer to do so
   using Ctrl + C. If that doesn't work, use other means as you deem
   fit.

6. You may hold the Shift key and right click in an empty area to use
   the "Open command window here" option.

7. If this is the only command-line program you use, you may also create
   a Powershell profile to automatically ``cd`` to this program's
   directory whenever you start Powershell. To do so, press Win + R,
   type ``%UserProfile%\Documents\`` to open your Documents folder.
   Therein, create a folder named ``WindowsPowerShell``. In this folder
   create a file named ``Microsoft.PowerShell_profile.ps1``. Edit this
   file to add all the commands you want to be executed whenever you
   start Powershell. Like the ``cd`` command mentioned in Tip #1.

   Start powershell and it would complain that execution of scripts is
   disabled. Execute the following command to take care of that:

       Set-ExecutionPolicy RemoteSigned

   Close and restart Powershell and you should find that it executed
   all the commands you entered in that *.ps1 file.

8. Install and use a linux distribution to get rid of all such pain. I
   would recommend Ubuntu_ for starters :-)

   .. _Ubuntu: http://www.ubuntu.com/


Author and Maintainer
---------------------

* Aditya <code.aditya (at) gmail>


License
-------

* GNU General Public License v3

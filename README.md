getmyancestors
==============

getmyancestors.py is a python3 script that downloads family trees in GEDCOM format from FamilySearch.

This program is now in production phase, but bugs might still be present. Features will be added on request. It is provided as is.

This script requires python3 and the requests module to work. To install this module on Linux, run in your terminal: "python3 -m pip install requests" (or "python3 -m pip install --user requests" if you don't have admin rights on your machine).

This script requires python 3.4 (or higher) to run due to some novel features in the argparse and asyncio modules (https://docs.python.org/3/whatsnew/3.4.html)

The graphical interface requires the tkinter module (https://docs.python.org/3/library/tkinter.html)

To download the script, click on the green button "Clone or download" on the top of this page and then click on "Download ZIP".

Current version was updated on May 13th 2018.


How to use
==========

With graphical user interface:

```
python3 fstogedcom.py
```

Command line examples:

Download four generations of ancestors for the main individual in your tree and output gedcom on stdout (will prompt for username and password):

```
python3 getmyancestors.py
```

Download four generations of ancestors and output gedcom to a file while generating a verbode stderr (will prompt for username and password):

```
python3 getmyancestors.py -o out.ged -v
```

Download four generations of ancestors for individual LF7T-Y4C and generate a verbose log file:

```
python3 getmyancestors.py -u username -p password -i LF7T-Y4C -o out.ged -l out.log -v
```

Download six generations of ancestors for individual LF7T-Y4C and generate a verbose log file:

```
python3 getmyancestors.py -a 6 -u username -p password -i LF7T-Y4C -o out.ged -l out.log -v
```

Download four generations of ancestors for individual LF7T-Y4C including all their children and their children spouses:

```
python3 getmyancestors.py -d 1 -m -u username -p password -i LF7T-Y4C -o out.ged
```

Download six generations of ancestors for individuals L4S5-9X4 and LHWG-18F including all their children, grandchildren and their spouses:

```
python3 getmyancestors.py -a 6 -d 2 -m -u username -p password -i L4S5-9X4 LHWG-18F -o out.ged
```

Download four generations of ancestors for individual LF7T-Y4C including LDS ordinances (need LDS account)

```
python3 getmyancestors.py -c -u username -p password -i LF7T-Y4C -o out.ged
```
Support
=======

Send questions, suggestions, or feature requests to benoitfontaine.ba@gmail.com or giulio.genovese@gmail.com

Theodore Novak - tjnovak - 1656602 - CSE 150 Final Project

A Python program that issues HTTP GET requests using the socket library,
modeled after the curl command line utility.  

Submission Contents:

1) README.txt: 
A text document which provides personal information, a short project description,
and brief descriptions of each of the project deliverables.

2) tjnovakMyCurl.py:
The Python program file that makes use of the socket library to issue HTTP GET
requests to web servers. It provides short feedback for the connection in the 
command window, appends an entry with connection details to the log file, and
copies the retrieved HTML document to HTTPoutput.html upon successful retrieval. 

3) Log.csv:
A csv file that provides more detailed information on each attempted HTTP connection
from tjnovakMyCurl.py. Each row corresponds to an entry, containing source and
destination IP addresses and ports, the HTTP server response line and status code,
the requested url and hostname, and whether the success was overall successful or not.

4) Discussion.pdf:
A text document discussing program usage, shortcomings, and the connections detailed in
the Log.csv deliverable. Wireshark packet captures have been provided for each of the 
logged connections, and the results of each of the connections are compared against that
of the curl command line utility. 

5) Questions.pdf:
A text document addressing questions related to project implementation, such as what
socket type was used, how destination ports were chosen, and how errors were handled.
Other questions inquire about termination of the program and the resulting outcome of
the TCP connection, why unsuccessful URLs failed, and the outcome of attempted HTTPS
connections.

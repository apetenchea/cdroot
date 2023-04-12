# Leaderless total-order broadcast algorithm

This is an implementation of a leaderless total-order broadcast algorithm, which serves as an example for my article,
[Time in Distributed Systems](https://apetenchea.github.io/2022/11/22/time-in-distributed-systems/).  

## Brief description

A distributed key-value store is simulated, where each node is a process that can send and receive messages. We 
achieve total-order using Lamport clocks and FIFO broadcast. The user can send a message to any of the
available nodes, and the algorithm makes sure the data gets reliably to all replicas.  Please note that when a message is broadcast, it is
also send to the sender. In the end, the user can check that all nodes have the same data.  
The architecture is composed of three layers:
- network layer, responsible for receiving, acknowledging and sending messages
- middleware layer, responsible for handling the order in which messages are delivered to the application
- application layer, responsible for the actual application logic, in our case, a key-value store

For details, please see the [Lamport Clocks](https://apetenchea.github.io/2022/11/22/time-in-distributed-systems/#Lamport-clocks)
section of the article.

## Running

First, make sure you have the required Python packages installed:
```
pip install -r requirements.txt
```
Then, if you're on Linux, use the `start.sh` helper to start a cluster with 3 replicas, passing the ports as arguments:
```
./start.sh 9000 9001 9002
```
Or, if you're on Windows, you can use the `start.ps1` helper from PowerShell:
```
.\start.ps1 9000,9001,9002
``` 
Start sending messages to the cluster, for example, 100 rounds of 3 messages in parallel each:
```
python test.py --ports 9000 9001 9002 --chaos 100 --parallel 3
```
In the end, check that all nodes have the same data:
```
python test.py --ports 9000 9001 9002 --check
```

To kill all running replicas, use the following command (warning, this will kill all running Python processes):
- Linux: `pkill python`
- Windows: `taskkill /f /im python.exe` 

## Practical considerations

Note that this is not a production-ready implementation. It is meant to be a simple example of a leaderless
total-order broadcast algorithm, for educational purposes. It is not fault-tolerant, and it does not handle adding or removing nodes.
Also, it was not designed for performance, but rather for correctness and simplicity.
# Main raylet - Main worker
1. REPL to ipc main raylet
2. Get worker
3. Worker = Local
4. RunTask in background
    4.1 Save result
5. Broadcast dataref in background
6. Return dataref

# Main raylet - Remote worker
1. REPL to ipc main raylet
2. Get worker
3. Worker = Remote
4. Send RunReq to remote ws
    4.1 Receive RunReq
    4.2 RunTask in background
        4.2.1 Save result
    4.3 Broadcast dataref in background
5. Return result to main
6. Return dataref

# Explanation
RunTaskLocal and RunTaskRemote can NOT have the same abstraction because
(assuming node A calls runTask to node B)
1. The datastore operation is different.
    Running in Local, means dataref should point to the future.
    Running in Remote, means dataref should point to remote node. And let that remote node decide and await for the task to finish.
2. Broadcasting dataref
    Who should broadcast the dataref? If it's RunTaskRemote and node A broadcasts the dataref, then the value (future/loc) may be conflict with the node B operation. We decide that the broadcaster should be the node that run the task.
3. Serialization consistency
    Serialization consistency guarantees that if user calls ref = task.remote(arg) to the node. Then calling ref.get() to that node again should guarantee the correct action (await, remote or return data)
    As RunTaskLocal, the task can be issued as future, then dataref can be created.
    As RunTaskRemote, if dataref is created before the tasks is sent to B then it's possible that the user may encounter error (Ref not found). Pairing with the decision to make B a broadcaster, the call to RunTaskRemote should be blocking to ensure that broadcasting is finished before returning the dataref to user.
4. Why not centralized at main raylet
    In conclusion, apart from acquiring and freeing the worker, there is no other logic at main raylet. So centralizing at main raylet will only be another complicated relay between local node (which create task) and remote node (that's going to run the task).

    Since we could not do abstraction on RunTaskLocal and RunTaskRemote, the logic is already transparent in ipc receiver function, we have no intention to further duplicate the logic into main raylet websocket again. Assuming, instead of just acquireWorker from main raylet, we sent the whole task for main raylet to handle, then we will be in the trouble - who should broadcast the dataref? If it's remote node with the assigned worker then we have to relay response from that remote node to main to local raylet. If it's main node the broadcaster, then we are in complicated consistency/race condition issue.

## As a result:
## RunTaskLocal
- Create dataref
- Create the task as future
    - Run the task
    - Store the result value back into the dataref
- Store dataref and future into datastore
- Broadcasting dataref
- Return dataref
## RunTaskRemote
- Create dataref
- Create the blocking task
    - Call remote RunTask through websocket
    - (Remote node) Create the task as future
        - Run the task
        - Store the result value back into the dataref
    - Store dataref and future into datastore
    - Broadcasting dataref
    - Return status
- (Store dataref (with remote node location) into datastore) - Done through broadcasting
- Return dataref

1. Complexity
    Ray isn't a good baseline to compare with Volpy because its complexity is very high.
    This is known and documented as Ray aims for very high performance.
    Since Volpy is a simple POC, we also need to write another simple native system as well.
    So right now, Volpy can support both native and browser computation.

2. Data
    Current Volpy provides no garbage collector / retain / release.

3. The implementation details
    Programming
        - Ray has many part writing in c, while Volpy writes most of the modules in Python.
    Concurrency
        Ray uses many kind of synchronization design (eventloop, queue, producer-consumer, etc.) and locks. For Volpy, we keep it as reasonably simple as possible.
    Data encoding and format
        There is no documentation on exact encoding and data format in Ray document. We only know that they use cloudpickle to serialize both the data and the task.
        In Volpy, we also follow the similar approach. However, in websocket module, we use JSON as a message between Raylet node.

4. Decentralized/Centralized Scheduler
    Ray scheduler is decentralized. The local scheduler can decide which worker to run the task without having to forward it to the main raylet.
    Volpy current scheduler is centralized. This is not really a downside of Volpy as decentralize/centralize approach is a trade-off between latency and consistency. We design our system this way to keep our design simple and prevent 

5. Scheduler Algorithm
    Volpy currently uses only Round-Robin algorithm, but the scheduling algorithm can be easily plugged-in and customized.

6. GPU support
    Volpy has no GPU supports.

7. Actor class (Stateful computation)
    Volpy has no Actor class.

8. Error handling and task cancellation
    Volpy has no error handling on some functions
        - broadcasting and maintaining consistency of dataref on raylet nodes
    Volpy doesn't provide task cancellation.

9. Latency
    Ray designs the system for cluster.
    While Volpy designs the system for voluntary grid computing. As a result, Volpy naturally has higher network latency than Ray and may not be able to support the same task or algorithm.
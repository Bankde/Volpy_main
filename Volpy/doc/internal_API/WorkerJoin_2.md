```mermaid
graph TD
    subgraph node1
        subgraph process_driver
            REPL
        end
        subgraph process_raylet_1
            raylet_IPC_1
            raylet_scheduler_1
            raylet_WS_1
        end
        subgraph process_worker_11
            worker_IPC_11
        end
        subgraph process_worker_12
            worker_IPC_12
        end
    end
    subgraph node2
        subgraph process_raylet_2
            raylet_IPC_2
            raylet_scheduler_2
            raylet_WS_2
        end
        subgraph process_worker_21
            worker_IPC_21
        end
        subgraph process_worker_22
            worker_IPC_22
        end
        worker_IPC_21 -- 1_initWorker --> raylet_IPC_2
        raylet_IPC_2 -- 2_saveToScheduler --> raylet_scheduler_2
        raylet_scheduler_2 -- 3 --> raylet_WS_2
        raylet_WS_2 -- 4 --> raylet_scheduler_2
        raylet_scheduler_2 -- 5 --> raylet_IPC_2
        raylet_IPC_2 -- 5_initTask --> worker_IPC_21

    end
    raylet_WS_2 -- 3_initWorker_ws --> raylet_WS_1
    raylet_WS_1 -- 3 --> raylet_scheduler_1
    raylet_scheduler_1 -- 4 --> raylet_WS_1
    raylet_WS_1 -- 4_response_workerId --> raylet_WS_2

    style process_driver fill:#FFCCCC,stroke:#660000,stroke-width:4px
    style process_raylet_1 fill:#CCFFCC,stroke:#006600,stroke-width:4px
    style process_worker_11 fill:#CCCCFF,stroke:#000066,stroke-width:4px
    style process_worker_12 fill:#CCCCFF,stroke:#000066,stroke-width:4px
```
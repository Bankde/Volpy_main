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
        worker_IPC_11 -- 1_initWorker --> raylet_IPC_1
        raylet_IPC_1 -- 2_saveToScheduler --> raylet_scheduler_1
        raylet_scheduler_1 -- 3 --> raylet_IPC_1
        raylet_IPC_1 -- 3_initTask --> worker_IPC_11
    end
    subgraph node2
    end

    style process_driver fill:#FFCCCC,stroke:#660000,stroke-width:4px
    style process_raylet_1 fill:#CCFFCC,stroke:#006600,stroke-width:4px
    style process_worker_11 fill:#CCCCFF,stroke:#000066,stroke-width:4px
    style process_worker_12 fill:#CCCCFF,stroke:#000066,stroke-width:4px
```
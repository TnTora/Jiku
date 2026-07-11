import { invalidateAll } from "$app/navigation"
import { page } from "$app/state"
import { getContext, setContext } from "svelte"
import { SvelteMap } from "svelte/reactivity"

export interface Task {
    id: string
    name: string
    total: number
    progress: number
    status: string
    controller?: AbortController
}

interface Progress {
    current: number
    total: number
}

interface TaskProgress<ResultType> {
    status: string
    result: ResultType | null
    traceback: string | null
    children: string | null
    date_done: string | null
    task_id: string
    name: string
}

export class TaskEventSource {
    url: string;
    src: EventSource | null = null;
    tasks: SvelteMap<string, Task>;
    tasks_finished;

    constructor(url: string) {
        this.url = url;
        this.tasks = new SvelteMap<string, Task>();
        this.tasks_finished = $derived.by(() => {
            let success = 0;
            let fail = 0;
            for (const [task_id, task] of this.tasks) {
                if (task.status == "SUCCESS") {
                    success++;
                } else if (task.status == "FAILURE") {
                    fail++;
                }
            }
            return {
                success: success,
                fail:fail
            };
        })
        // $effect(() => {
        //     console.log(this.tasks);
        // })
    }

    connect() {
        if (this.src) { return; }

        this.src = new EventSource(this.url);
        this.src.onopen = this.handleOpen.bind(this);
        this.src.onerror = this.handleErrors.bind(this);
        this.src.onmessage = this.handleMessage.bind(this);
        this.src.addEventListener("close", this.handleClose.bind(this));
    }

    disconnect() {
        this.src?.close();
        this.src = null;
    }

    handleMessage(event: MessageEvent) {
        const data: TaskProgress<Progress> = JSON.parse(event.data);
        // console.log(data);
        let task = this.tasks.get(data.task_id);
        if (task) {
            if (data.status == "CANCELLED" || data.status == "REVOKED") {
                this.removeTask(data.task_id);
            } else {
                this.updateTask(task, data);
            }
        } else {
            this.addTask(data);
        }
    }

    createTask(name: string) {
        const task = $state({
            id: crypto.randomUUID(),
            name: name,
            status: "UPLOADING",
            total: -1,
            progress: 0,
            controller: new AbortController(),
        });
        this.tasks.set(task.id, task);
        return task;
    }

    addTask(data: TaskProgress<Progress> ) {
        const task = $state({
            id: data.task_id,
            name: data.name,
            status: data.status,
            total: -1,
            progress: 0,
        });

        if (data.result) {
            task.total = data.result.total;
            task.progress = data.result.current;
        }
        this.tasks.set(task.id, task);
    }

    updateTask(task: Task, data: TaskProgress<Progress> ) {
        task.status = data.status;
        if ((task.status == "PROGRESS") && (data.result)) {
            task.total = data.result.total;
            task.progress = data.result.current;
        }
        if (task.status == "SUCCESS"){
            console.log("task success");
            if (page.url.pathname === "/books") {
                invalidateAll();
            }
        }
    }

    clearFinished() {
        for (const [task_id, task] of this.tasks) {
            if (task.status == "SUCCESS" || task.status == "FAILURE") {
                this.removeTask(task_id);
            }
        }
    }

    async closeTask(task_id: string) {
        const task = this.tasks.get(task_id);
        if (!task) { return; }

        if (task.status == "UPLOADING") {
            task.controller?.abort();
            this.removeTask(task.id);
            return;
        }

        if (task.status == "SUCCESS" || task.status == "FAILURE") {
            this.removeTask(task.id);
            return;
        }

        const res = await fetch("/api_bridge/books/stop_book_processing", {
            method:"PUT",
            headers: {
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                id: task.id
            }),
        });
    }

    stopUploads() {
        for (const [task_id, task] of this.tasks) {
            if (task.status == "UPLOADING") {
                task.controller?.abort();
                this.removeTask(task_id);
            }
        }
    }

    handleErrors(error: Event) {
        console.error("Error while listening to task events", error);
        console.log("Disconnecting task event source...");
        this.disconnect();
    }

    handleOpen() {
        console.log("Listening to task events");
    }

    handleClose() {
        console.log("Tasks Events stopped");
        this.disconnect();
    }

    removeTask(task_id: string) {
        this.tasks.delete(task_id);
    }

}

const TASKS_CONTEXT_KEY = Symbol("TASKS");

export function setTasksContext(url: string) {
    return setContext(TASKS_CONTEXT_KEY, new TaskEventSource(url));
}

export function getTasksContext() {
    return getContext<ReturnType<typeof setTasksContext>>(TASKS_CONTEXT_KEY);
}


interface SyncMorphsProgress {
    current_rule_name: string
    current_rule: number
    total_rules: number
    current_note: number
    total_notes: number
}

export interface SyncTask {
    id: string
    progress: SyncMorphsProgress
    status: string
}


export class SyncMorphsEventSource {
    url: string;
    src: EventSource | null = null;
    sync_task: SyncTask | null = $state(null);

    constructor(url: string) {
        this.url = url;
    }

    connect() {
        if (this.src) { return; }

        this.src = new EventSource(this.url);
        this.src.onopen = this.handleOpen.bind(this);
        this.src.onerror = this.handleErrors.bind(this);
        this.src.onmessage = this.handleMessage.bind(this);
        this.src.addEventListener("close", this.handleClose.bind(this));
    }

    disconnect() {
        this.src?.close();
        this.src = null;
        this.sync_task = null;
    }

    handleMessage(event: MessageEvent) {
        const data: TaskProgress<SyncMorphsProgress> = JSON.parse(event.data);
        console.log(data);
        if (this.sync_task && data.result) {
            this.sync_task.progress = data.result;
        } else {
            let tmp_progress: SyncMorphsProgress;

            if (data.result) {
                tmp_progress = data.result;
            } else {
                tmp_progress = {
                    current_rule_name: "",
                    current_rule: 0,
                    total_rules: -1,
                    current_note: 0,
                    total_notes: -1,
                }
            }

            this.sync_task = {
                id: data.task_id,
                progress: tmp_progress,
                status: data.status,
            }
        }
    }

    handleErrors(error: Event) {
        console.error("Error while listening to sync events", error);
        console.log("Disconnecting sync event source...");
        this.disconnect();
    }

    handleOpen() {
        console.log("Listening to sync events");
    }

    handleClose() {
        console.log("Sync Events stopped");
        invalidateAll();
        this.disconnect();
    }

}


const SYNC_TASK_CONTEXT_KEY = Symbol("SYNC_TASK");

export function setSyncTaskContext(url: string) {
    return setContext(SYNC_TASK_CONTEXT_KEY, new SyncMorphsEventSource(url));
}

export function getSyncTasksContext() {
    return getContext<ReturnType<typeof setSyncTaskContext>>(SYNC_TASK_CONTEXT_KEY);
}
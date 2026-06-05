import { getContext, setContext } from "svelte"
import { SvelteMap } from "svelte/reactivity"

export interface Task {
    id: string
    name: string
    total: number
    progress: number
    status: string
}

interface Progress {
    current: number
    total: number
}

interface TaskProgress {
    status: string
    result: Progress | null
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

    constructor(url: string) {
        this.url = url;
        this.tasks = new SvelteMap<string, Task>();
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
        const data: TaskProgress = JSON.parse(event.data);
        console.log(data);
        let task = this.tasks.get(data.task_id);
        if (task) {
            this.updateTask(task, data);
        } else {
            this.addTask(data);
        }
    }

    addTask(data: TaskProgress) {
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

    updateTask(task: Task, data: TaskProgress) {
        task.status = data.status;
        if ((task.status == "PROGRESS") && (data.result)) {
            task.total = data.result.total;
            task.progress = data.result.current;
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

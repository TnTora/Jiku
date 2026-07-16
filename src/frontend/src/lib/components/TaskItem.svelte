<script lang="ts">
	import type { Task } from "$lib/utils/taskEventSource.svelte";
    import { getTasksContext } from "$lib/utils/taskEventSource.svelte";

    const task_context = getTasksContext();

    interface Props {
        task: Task
    }

    let { task }: Props = $props();
    let btn_shared_classes = "hover:text-sky-700 active:text-sky-500 hover:cursor-pointer";

</script>

<div id={task.id} class="item-grid p-1 bg-neutral-600 rounded-md">
    <span class="truncate" style="grid-area:name">{task.name}</span>
    <span style="grid-area:progress">Status: {task.status} Progress: {task.progress}/{(task.total > 0)? task.total : "?"}</span>
    <button
        class="{btn_shared_classes} mx-2"
        style="grid-area:close"
        title="Close Task"
        onclick={() => {task_context.closeTask(task.id)}}
    >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6" viewBox="0 0 15 15">
            <path fill="currentColor" d="M3.64 2.27L7.5 6.13l3.84-3.84A.92.92 0 0 1 12 2a1 1 0 0 1 1 1a.9.9 0 0 1-.27.66L8.84 7.5l3.89 3.89A.9.9 0 0 1 13 12a1 1 0 0 1-1 1a.92.92 0 0 1-.69-.27L7.5 8.87l-3.85 3.85A.92.92 0 0 1 3 13a1 1 0 0 1-1-1a.9.9 0 0 1 .27-.66L6.16 7.5L2.27 3.61A.9.9 0 0 1 2 3a1 1 0 0 1 1-1c.24.003.47.1.64.27" />
        </svg>
    </button>
</div>

<style>

.item-grid {
    display: grid;
    /* column-gap: 0.75rem; */
    grid-template-columns: 1fr auto;
    grid-template-areas:
    "name close"
    "progress close"
}

</style>
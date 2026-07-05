<script lang="ts">
    import TaskItem from "./TaskItem.svelte";
    import { getTasksContext } from "$lib/utils/taskEventSource.svelte";

    const task_context = getTasksContext();
    let show_tasks = $state(false);
    let btn_shared_classes = "hover:text-sky-700 active:text-sky-500 hover:cursor-pointer";
</script>

<div class="absolute bottom-7 left-3 p-2 bg-neutral-700 border-neutral-600 border rounded-md z-50">
    {#if show_tasks}
        <div class="flex justify-between items-center gap-2">
            <span class="font-bold text-md">Tasks</span>
            <button class="text-sm hover:text-sky-600 active:text-sky-500 cursor-pointer">clear all</button>
            <button class="mx-2 hover:text-red-700 active:text-red-500 hover:cursor-pointer" style="grid-area:close" title="Hide Tasks" onclick={() => { show_tasks = false; }}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6" viewBox="0 0 15 15">
                    <path fill="currentColor" d="M3.64 2.27L7.5 6.13l3.84-3.84A.92.92 0 0 1 12 2a1 1 0 0 1 1 1a.9.9 0 0 1-.27.66L8.84 7.5l3.89 3.89A.9.9 0 0 1 13 12a1 1 0 0 1-1 1a.92.92 0 0 1-.69-.27L7.5 8.87l-3.85 3.85A.92.92 0 0 1 3 13a1 1 0 0 1-1-1a.9.9 0 0 1 .27-.66L6.16 7.5L2.27 3.61A.9.9 0 0 1 2 3a1 1 0 0 1 1-1c.24.003.47.1.64.27" />
                </svg>
            </button>
        </div>
        <div class="mt-2 max-h-[min(30rem,calc(100vh-3rem))] overflow-y-scroll flex p-2 flex-col gap-1">
            {#each task_context.tasks as [task_id, task]}
                <TaskItem {task} />
            {/each}
        </div>
    {:else}
        <button class="{btn_shared_classes} mx-2" style="grid-area:close" title="Show Tasks" onclick={() => { show_tasks = true; }}>
            <svg class="h-6" xmlns="http://www.w3.org/2000/svg" width="1.28em" height="1em" viewBox="0 0 1792 1408">
                <path d="M0 0h1792v1408H0z" fill="none" />
                <path fill="currentColor" d="M1024 1280h640v-128h-640zM640 768h1024V640H640zm640-512h384V128h-384zm512 832v256q0 26-19 45t-45 19H64q-26 0-45-19t-19-45v-256q0-26 19-45t45-19h1664q26 0 45 19t19 45m0-512v256q0 26-19 45t-45 19H64q-26 0-45-19T0 832V576q0-26 19-45t45-19h1664q26 0 45 19t19 45m0-512v256q0 26-19 45t-45 19H64q-26 0-45-19T0 320V64q0-26 19-45T64 0h1664q26 0 45 19t19 45" />
            </svg>
            
        </button>
    {/if}
</div>
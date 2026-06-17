<script lang="ts">
    import { getSyncTasksContext } from "$lib/utils/taskEventSource.svelte";

    let { known_morphemes } = $props()

    let sync_task_context = getSyncTasksContext();

    async function startSync() {
        sync_task_context.connect();
        const tmp_progress = {
                    current_rule_name: "",
                    current_rule: 0,
                    total_rules: -1,
                    current_note: 0,
                    total_notes: -1,
                }
        sync_task_context.sync_task = {
            id: "tmp",
            progress: tmp_progress,
            status: "WAITING",
        };
        const res = await fetch("http://127.0.0.1:8000/anki/sync_morphemes", {
            method: "PUT"
        });
    }

</script>

<div class="flex items-center bg-sky-500 w-fit rounded-b-md">
    <button
        class="bg-sky-600 hover:bg-sky-700 active:bg-sky-800 cursor-pointer px-2 py-1 rounded-bl-md"
        title="Sync Morphs"
        onclick={startSync}    
    >
        Sync
    </button>
    <button class="mx-2 cursor-pointer">
        Lemmas: {known_morphemes.lemmas}
    </button>
    <span>|</span>
    <button class="mx-2 cursor-pointer">
        Inflections: {known_morphemes.inflections}
    </button>
</div>
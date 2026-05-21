<script lang="ts">
let { use_input = false, text_input_value = $bindable(null), text_input_default = "", text, onOk, onCacncel } = $props()

</script>

<div class="w-full h-full bg-neutral-800/90 absolute flex items-center justify-center">
    <div class="p-4 bg-[#1B1B1B] border border-neutral-900 rounded-2xl flex flex-col text-center items-center justify-center gap-3">
        <p>{text}</p>
        {#if use_input}
            <input bind:value={text_input_value} type="text" defaultvalue={text_input_default} class="text-center bg-neutral-800 rounded-md">
        {/if}
        <div class="flex items-center justify-evenly gap-4">
            <button
                class="px-3 py-1 w-20 bg-neutral-800 rounded-full text-sm font-semibold hover:bg-neutral-700 active:bg-neutral-600"
                onclick={onOk}
            >
                Ok
            </button>
            <button
                class="px-3 py-1 w-20 bg-neutral-800 rounded-full text-sm font-semibold hover:bg-neutral-700 active:bg-neutral-600"
                onclick={onCacncel}>
                Cancel
            </button>
        </div>
        
    </div>
</div>
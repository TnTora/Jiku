<script lang="ts">
    interface Option {
        name: string,
        value: any,
    }

    interface Props {
        options: Option[],
        selected_name?: string,
        selected_value?: any,
    }

    let { options, selected_name = $bindable(), selected_value = $bindable() }: Props = $props();
    
    selected_name = options.filter((option) => option.value == selected_value)[0].name;

</script>

<div class="grid container items-center justify-center gap-0.5 bg-neutral-950 border-neutral-950 border rounded-md overflow-hidden"
    style="--opt-length: {options.length};">
    {#each options as option}
        <button 
            onclick={() => {(selected_name = option.name, selected_value = option.value)}}
            class="bg-neutral-500 w-full h-full flex items-center justify-center {(selected_name == option.name)? "selected bg-[#0062ff]!": ""}"
        >
            <span>{option.name}</span>
        </button>
    {/each}
</div>

<style>

.container {
    --opt-length: 2;
    grid-template-columns: repeat(var(--opt-length), minmax(0, 1fr));
    height: var(--height, auto);
}

</style>
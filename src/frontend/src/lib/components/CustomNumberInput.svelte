<script lang="ts">

    interface Props {
        value: number,
        id: string,
        left_text?: string,
        right_text?: string,
        left_fn: () => void,
        right_fn: () => void,
        left_style?: string,
        right_style?: string,
        value_style?: string,
    }

    let {
        value = $bindable(),
        id,
        left_fn,
        right_fn,
        left_text = "-",
        right_text = "+",
        left_style = "",
        right_style = "",
        value_style = "",
    }: Props = $props();

</script>

<div class="flex items-center mx-auto border border-neutral-600 bg-neutral-600 rounded-full">
    <button onclick={left_fn} class="w-7 h-7 pl-1 rounded-l-full cursor-pointer bg-neutral-700 active:bg-neutral-600" style={left_style}>{left_text}</button>
    <input id={id} type="number" bind:value={value} class="w-9 h-7 text-sm text-center hide-input-spinners z-10" style={value_style}>
    <button onclick={right_fn} class="w-7 h-7 pr-1 rounded-r-full cursor-pointer bg-neutral-700 active:bg-neutral-600" style={right_style}>{right_text}</button>
</div>

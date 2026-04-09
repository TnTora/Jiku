<script lang="ts">
    let { errors } = $props();

    function onclick () {
        errors.pop();
    }

</script>

{#if errors.length > 0}
    <div class="min-w-2xs max-w-[500px] min-h-12 bg-red-500 border border-red-300 rounded-full text-white absolute top-3 z-50 left-[50%] -translate-x-[50%] grid grid-cols-[1fr_auto_1fr] grid-rows-[1fr_auto_1fr] items-center gap-x-1.5">
        <div class="row-span-full col-start-1 flex">
            <div class="ml-3 px-2 bg-red-300 min-w-6 rounded-full">{errors.length}</div>
        </div>
        <div class="row-[1/4] col-start-2 text-center">
            <div class="text-sm ">{errors[errors.length-1].short?? "Error"}</div>
        </div>
        <div class="row-span-full col-start-3 flex justify-end">
            <button {onclick} class="mr-5 hover:text-neutral-700 hover:cursor-pointer">X</button>
        </div>
        {#if errors[errors.length-1].details}
            <div class="row-start-2 col-start-2 text-center">{false? errors[errors.length-1].details: ""}</div>
            <div class="row-start-3 col-start-2 text-[0.5rem] h-full text-center flex flex-col justify-end ">
                <div class="hover:text-neutral-700 hover:cursor-pointer">Show Details</div>
            </div>
        {/if}
    </div>
{/if}
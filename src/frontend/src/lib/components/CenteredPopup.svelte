<script lang="ts">
    let { children } = $props()
    
    </script>
    
    <div class="popup w-screen h-screen bg-neutral-800/90 fixed top-0 left-0 flex items-center justify-center z-50">
        <div class="p-4 bg-[#1B1B1B] border border-neutral-900 rounded-2xl flex flex-col text-center items-center justify-center gap-3">
            {@render children()}
        </div>
    </div>
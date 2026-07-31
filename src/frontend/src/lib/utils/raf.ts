export function createRafHandler(): ((callback: () => void) => void) {
    let req_id: number | null = null;
    let _callback: (() => void) | null = null;

    return function (callback: () => void) {
        _callback = callback;
        if (req_id === null) {
            req_id = requestAnimationFrame(() => {
                req_id = null;
                if (_callback) {
                    _callback();
                    _callback = null;
                }
            });
        }
    }
}
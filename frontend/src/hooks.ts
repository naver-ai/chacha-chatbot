import { useEffect, useState } from "react";

export function useOnMountRendered(enabled: boolean): boolean {
    const [isRendered, setIsRendered] = useState(false);    
    
    useEffect(() => {
            if (enabled) {
                const timer = setTimeout(() => setIsRendered(true), 100);
                return () => clearTimeout(timer);
            } else {
                setIsRendered(false);
            }
        }, [enabled]);

    return isRendered
}
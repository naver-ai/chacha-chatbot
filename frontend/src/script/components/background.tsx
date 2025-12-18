import { useEffect, useState } from 'react';

const poweredByHCXLogoURL = new URL('../../assets/powered_by_hcx.svg', import.meta.url);
const nccLogoURL = new URL('../../assets/ncc_logo.svg', import.meta.url);
const vignetteLeftURL = new URL('../../assets/vignette_vert_left.svg', import.meta.url);
const vignetteRightURL = new URL('../../assets/vignette_vert_right.svg', import.meta.url);

export const BackgroundPanel = ({
    showVignette = false,
    vignetteWidth = 180,
    scrollContainer
}: {showVignette?: boolean, vignetteWidth?: number, scrollContainer?: string}) => {
    
    const [scrollY, setScrollY] = useState(0);
    
    useEffect(() => {
        const handleScroll = (event?: Event) => {
            if (scrollContainer) {
                const container = document.getElementById(scrollContainer);
                if (container) {
                    setScrollY(container.scrollTop);
                } else {
                    setScrollY(window.scrollY);
                }
            } else {
                setScrollY(window.scrollY);
            }
        };
        
        if (scrollContainer) {
            const container = document.getElementById(scrollContainer);
            if (container) {
                container.addEventListener('scroll', handleScroll);
                return () => container.removeEventListener('scroll', handleScroll);
            }
        }
        
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [scrollContainer]);

        return <>
            <div className="background-panel fixed top-0 left-0 right-0 bottom-0 z-[-1] pointer-events-none"/>
            <img className={"absolute right-8 bottom-4 hidden lg:block"} src={poweredByHCXLogoURL.href} alt={"Powered by HyperCLOVA X"} width={250}/>
            <img className={"absolute left-8 bottom-5 hidden lg:block"} src={nccLogoURL.href} alt={"NCC Logo"} width={150}/>
            {showVignette && <>
                <div 
                    className="hidden lg:block pointer-events-none absolute left-0 top-1/2 opacity-40"
                    style={{ transform: `translateY(-50%)` }}
                >
                    <img 
                        src={vignetteLeftURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * 0.05}px)` }}
                    />
                    <img 
                        src={vignetteLeftURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * 0.08}px)` }}
                    />
                    <img 
                        src={vignetteLeftURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * 0.12}px)` }}
                    />
                </div>
                <div 
                    className="hidden lg:block pointer-events-none absolute right-0 top-1/2 opacity-40"
                    style={{ transform: `translateY(-50%)` }}
                >
                    <img 
                        src={vignetteRightURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * 0.05}px)` }}
                    />
                    <img 
                        src={vignetteRightURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * 0.08}px)` }}
                    />
                    <img 
                        src={vignetteRightURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * 0.12}px)` }}
                    />
                </div>
            </>}
        </>
}
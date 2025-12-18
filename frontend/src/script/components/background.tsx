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
    const [isVignetteVisible, setIsVignetteVisible] = useState(false);
    
    useEffect(() => {
        let animationFrameId: number;
        
        const handleScroll = (event?: Event) => {
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
            
            animationFrameId = requestAnimationFrame(() => {
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
            });
        };
        
        if (scrollContainer) {
            const container = document.getElementById(scrollContainer);
            if (container) {
                container.addEventListener('scroll', handleScroll, { passive: true });
                return () => {
                    container.removeEventListener('scroll', handleScroll);
                    if (animationFrameId) {
                        cancelAnimationFrame(animationFrameId);
                    }
                };
            }
        }
        
        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => {
            window.removeEventListener('scroll', handleScroll);
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
        };
    }, [scrollContainer]);

    useEffect(() => {
        if (showVignette) {
            const timer = setTimeout(() => setIsVignetteVisible(true), 100);
            return () => clearTimeout(timer);
        } else {
            setIsVignetteVisible(false);
        }
    }, [showVignette]);

        return <>
            <div className="background-panel fixed top-0 left-0 right-0 bottom-0 z-[-1] pointer-events-none"/>
            {showVignette && <>
                <div 
                    className={`vignette-left hidden lg:block pointer-events-none absolute left-0 top-1/2 transition-all duration-700 ${
                        isVignetteVisible ? 'opacity-40 translate-x-0' : 'opacity-0 -translate-x-8'
                    }`}
                    style={{ transform: `translateY(-50%) ${isVignetteVisible ? 'translateX(0)' : 'translateX(-32px)'}` }}
                >
                    <img 
                        src={vignetteLeftURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * -0.05}px)` }}
                    />
                    <img 
                        src={vignetteLeftURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * -0.15}px)` }}
                    />
                    <img 
                        src={vignetteLeftURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * -0.12}px)` }}
                    />
                </div>
                <div 
                    className={`vignette-right hidden lg:block pointer-events-none absolute right-0 top-1/2 transition-all duration-700 ${
                        isVignetteVisible ? 'opacity-40 translate-x-0' : 'opacity-0 translate-x-8'
                    }`}
                    style={{ transform: `translateY(-50%) ${isVignetteVisible ? 'translateX(0)' : 'translateX(32px)'}` }}
                >
                    <img 
                        src={vignetteRightURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * -0.05}px)` }}
                    />
                    <img 
                        src={vignetteRightURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * -0.15}px)` }}
                    />
                    <img 
                        src={vignetteRightURL.toString()}
                        width={vignetteWidth}
                        style={{ transform: `translateY(${scrollY * -0.12}px)` }}
                    />
                </div>
            </>}
            <img className={"absolute right-8 bottom-4 hidden lg:block"} src={poweredByHCXLogoURL.href} alt={"Powered by HyperCLOVA X"} width={250}/>
            <img className={"absolute left-8 bottom-5 hidden lg:block"} src={nccLogoURL.href} alt={"NCC Logo"} width={150}/>
            
        </>
}
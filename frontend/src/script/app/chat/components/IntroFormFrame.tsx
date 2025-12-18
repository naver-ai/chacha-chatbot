import {useState, useEffect} from 'react'
import { useTranslation } from 'react-i18next'

const vignetteUpperURL = new URL('../../../../assets/vignette_upper.svg', import.meta.url).toString()
const vignetteLowerURL = new URL('../../../../assets/vignette_lower.svg', import.meta.url).toString()

export const IntroFormFrame = (props: {children?: any}) => {

    const [t] = useTranslation()
    const [isVisible, setIsVisible] = useState(false)

    const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
    useEffect(() => {
        // Trigger entering animation
        const timer = setTimeout(() => setIsVisible(true), 100)
        
        let rafId: number
        const handleMouseMove = (e: MouseEvent) => {
            if (rafId) return
            rafId = requestAnimationFrame(() => {
                const x = (e.clientX / window.innerWidth - 0.5) * 20
                const y = (e.clientY / window.innerHeight - 0.5) * 20
                setMousePos({ x: -x, y: -y })
                rafId = 0
            })
        }

        window.addEventListener('mousemove', handleMouseMove)
        return () => {
            clearTimeout(timer)
            window.removeEventListener('mousemove', handleMouseMove)
            if (rafId) cancelAnimationFrame(rafId)
        }
    }, [])

    return <div className="flex flex-col justify-between h-screen intro-form-frame">
        <div className="my-auto mx-auto flex flex-col items-center gap-y-4">
            <div className={`pointer-events-none absolute transition-all duration-700 delay-[400ms] ease-out ${
                isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-[70%]'
            }`}>
                <img 
                    src={vignetteUpperURL} 
                    className="translate-y-[-180px] opacity-70 transition-transform duration-300 ease-out" 
                    style={{ transform: `translate(${mousePos.x * 1.2}px, calc(-180px + ${mousePos.y * 1.3}px))` }}
                    width={500}
                />
            </div>
            <div className={`pointer-events-none absolute transition-all duration-700 delay-[300ms] ease-out ${
                isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-[70%]'
            }`}>
            <img 
                src={vignetteLowerURL} 
                className="translate-y-[120px] opacity-70 transition-transform duration-300 ease-out" 
                style={{ transform: `translate(${mousePos.x * 0.7}px, calc(120px + ${mousePos.y * 0.8}px))` }}
                width={500}
            />
            </div>
            <div className={`text-xl font-black z-10 transition-all duration-500 delay-200 ${
                isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}>{t("TITLE")}</div>
            <div className={`z-10 transition-all duration-500 delay-300 ${isVisible ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-4'}`}>{props.children}</div>
        </div>
    </div>
}
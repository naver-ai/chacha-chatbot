import {useState, useEffect} from 'react'
import { useTranslation } from 'react-i18next'

const vignetteUpperURL = new URL('../../../../assets/vignette_upper.svg', import.meta.url).toString()
const vignetteLowerURL = new URL('../../../../assets/vignette_lower.svg', import.meta.url).toString()

export const IntroFormFrame = (props: {children?: any}) => {

    const [t] = useTranslation()

    const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
    useEffect(() => {
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
            window.removeEventListener('mousemove', handleMouseMove)
            if (rafId) cancelAnimationFrame(rafId)
        }
    }, [])

    return <div className="flex flex-col justify-between h-screen intro-form-frame">
        <div className="my-auto mx-auto flex flex-col items-center gap-y-4">
            <img 
                src={vignetteUpperURL} 
                className="pointer-events-none absolute translate-y-[-180px] opacity-70 transition-transform duration-300 ease-out" 
                style={{ transform: `translate(${mousePos.x * 1.2}px, calc(-180px + ${mousePos.y * 1.3}px))` }}
                width={500}
            />
            <img 
                src={vignetteLowerURL} 
                className="pointer-events-none absolute translate-y-[120px] opacity-70 transition-transform duration-500 ease-out" 
                style={{ transform: `translate(${mousePos.x * 0.7}px, calc(120px + ${mousePos.y * 0.8}px))` }}
                width={500}
            />
            <div className="text-xl font-black z-10">{t("TITLE")}</div>
            <div className="z-10">{props.children}</div>
        </div>
    </div>
}
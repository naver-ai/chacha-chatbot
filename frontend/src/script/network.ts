import { ChatMessage } from "./types"

export class NetworkHelper{

    static readonly ENDPOINT_INITIALIZE = "/initialize"
    static readonly ENDPOINT_INFO = "/info"
    static readonly ENDPOINT_MESSAGES = "/messages"
    static readonly ENDPOINT_REGENERATE = "/regenerate"
    static readonly ENDPOINT_TERMINATE = "/terminate"
    static readonly ENDPOINT_MESSAGE = "/message"

    static readonly ENDPOINT_DOWNLOAD_CSV = "/download_csv"
    
    static readonly JSON_HEADERS = {
        "Content-Type": "application/json"
    }

    static makeChatAPIEndpointPrefix(sessionId: string): string {
        return (process.env.NODE_ENV == "development" ? "http://localhost:8000" : "") + "/api/v1/chat/sessions/" + sessionId
    }

    static makeEndpoint(sessionId: string, endpoint: string): string {
        return this.makeChatAPIEndpointPrefix(sessionId) + endpoint
    }

    static makeInitializeEndpointArgs(userName: string, userAge: number, locale?: string): object {
        return {
            user_name: userName,
            user_age: userAge,
            locale
        }
    }

    static async initializeSession(sessionId: string, userName: string, userAge: number, locale?: string): Promise<ChatMessage>{
        const resp = await fetch(this.makeEndpoint(sessionId, this.ENDPOINT_INITIALIZE),
            {
                method: 'POST',
                body: JSON.stringify(this.makeInitializeEndpointArgs(userName, userAge, locale)),
                headers: NetworkHelper.JSON_HEADERS
            }
        )
        if(resp.status === 200){
            return resp.json()
        }else throw Error(`Session initialization error - ${resp.status}`)
    }


    static async loadSessionChatMessages(sessionId: string): Promise<Array<ChatMessage>>{
        const resp = await fetch(this.makeEndpoint(sessionId, this.ENDPOINT_MESSAGES),
            {
                method: 'GET',
                headers: NetworkHelper.JSON_HEADERS
            }
        )
        if(resp.status === 200){
            return resp.json()
        }else throw Error(`Session initialization error - ${resp.status}`)
    }

    static async loadSessionInfo(sessionId: string): Promise<{user_name: string, user_age: number, locale: string}>{
        const resp = await fetch(this.makeEndpoint(sessionId, this.ENDPOINT_INFO),
            {
                method: 'GET',
                headers: NetworkHelper.JSON_HEADERS
            }
        )
        if(resp.status === 200){
            return resp.json()
        }else throw Error(`Session initialization error - ${resp.status}`)
    }


    static async sendUserMessage(sessionId: string, userMessage: ChatMessage): Promise<ChatMessage>{
        const resp = await fetch(this.makeEndpoint(sessionId, this.ENDPOINT_MESSAGE),
            {
                method: 'POST',
                body: JSON.stringify(userMessage),
                headers: NetworkHelper.JSON_HEADERS
            }
        )
        if(resp.status === 200){
            return resp.json()
        }else throw Error(`Send user message error - ${resp.status}`)
    }



    static async regenerateLastSystemMessage(sessionId: string): Promise<ChatMessage | undefined>{
        const resp = await fetch(this.makeEndpoint(sessionId, this.ENDPOINT_REGENERATE),
            {
                method: 'POST',
                headers: NetworkHelper.JSON_HEADERS
            }
        )
        if(resp.status === 200){
            return resp.json()
        }else throw Error(`regeneration error - ${resp.status}`)
    }
}
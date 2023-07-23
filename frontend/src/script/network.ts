import { ChatMessage } from "./types"

export class NetworkHelper{

    static readonly ENDPOINT_INITIALIZE = "/initialize"
    static readonly ENDPOINT_MESSAGES = "/messages"
    static readonly ENDPOINT_TERMINATE = "/terminate"
    static readonly ENDPOINT_MESSAGE = "/message"
    
    static readonly JSON_HEADERS = {
        "Content-Type": "application/json"
    }

    static makeChatAPIEndpointPrefix(sessionId: string): string {
        return (process.env.NODE_ENV == "development" ? "http://localhost:8000" : "") + "/api/v1/chat/sessions/" + sessionId
    }

    static makeEndpoint(sessionId: string, endpoint: string): string {
        return this.makeChatAPIEndpointPrefix(sessionId) + endpoint
    }

    static makeInitializeEndpointArgs(userName: string, userAge: number): object {
        return {
            user_name: userName,
            user_age: userAge
        }
    }

    static async initializeSession(sessionId: string, userName: string, userAge: number): Promise<ChatMessage>{
        const resp = await fetch(this.makeEndpoint(sessionId, this.ENDPOINT_INITIALIZE),
            {
                method: 'POST',
                body: JSON.stringify(this.makeInitializeEndpointArgs(userName, userAge)),
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
        }else throw Error(`Session initialization error - ${resp.status}`)
    }
}
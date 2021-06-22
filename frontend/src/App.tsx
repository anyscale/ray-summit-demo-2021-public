import { useRef } from 'react';
import './App.css';

import { Widget, addResponseMessage, toggleWidget, toggleMsgLoader, renderCustomComponent } from 'react-chat-widget';

import 'react-chat-widget/lib/styles.css';
import axios from 'axios';
import styled from 'styled-components';
import {
  BrowserRouter as Router,
  Link,
  useLocation
} from "react-router-dom";


addResponseMessage("Hello! I'm here to help answer questions you might have about Ray. What can I help you with today?")

const Wrapper = styled.div`
  overflow:hidden;
  width: 100vw;
  height: 100vh;
`

const Embed = styled.iframe`
  width: 100vw;
  height: 100vh;
  border: 0;
`

interface APIResponse {
  message: string;
  header: string;
  link: string;
}


const App = () => {
  return (
    <Router>
      <InnerApp />
    </Router>
  )
}

function InnerApp() {

  const pathname = useLocation().pathname

  const handleNewUserMessage = async (newMessage: string) => {
    toggleMsgLoader()
    const res = await axios.get("/chat", {
      params: {
        msg: newMessage
      }
    }).finally(() => {
      toggleMsgLoader()
    })

    const data = res.data
    // TEST DATA:
    // const data: APIResponse = {
    //   message: "Here",
    //   header: "API page",
    //   // link: "/en/master/package-ref.html"
    //   link: "https://www.google.com"
    // }

    renderCustomComponent(Message, data, true)
  };

  return (
    <Wrapper>

      <Embed src={`https://ray.io`} name="docs" />

      <Widget
        title="Ray Support Bot"
        subtitle="How can I help you today?"
        senderPlaceHolder="Ask me a question..."
        // fullScreenMode
        handleNewUserMessage={handleNewUserMessage}
      />
    </Wrapper>

  );
}

const Message = ({ message, link, header }: APIResponse) => {
  const d = new Date(); // for now
  const time = useRef(d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))

  const isLocalLink = !link.includes("http")
  const pathname = useLocation().pathname

  return <>
    <div className="rcw-response">
      <div className="rcw-message-text">
        <p>{message}</p>
        {isLocalLink ?
          <Link to={link} onClick={() => {
            if (link.includes(pathname)) {
              // Force a reload
              (window.frames["docs" as any] as any).location = `https://docs.ray.io${link}`
            }
          }}> {header} </Link>
          : <a href={link} target="_blank" rel="noreferrer">{header}</a>
        }

      </div>
      <span className="rcw-timestamp">{time.current}</span>
    </div>
  </>
}

export default App;

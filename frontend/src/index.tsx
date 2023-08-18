import React from 'react';
import {createRoot} from 'react-dom/client';
import './i18n';
import { App } from 'src/script/App';

const container = document.getElementById("app")
const root = createRoot(container!)
root.render(<React.StrictMode><App/></React.StrictMode>);
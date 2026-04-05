import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import Landing from "./pages/Landing";
import Environment from "./pages/Environment";
import Tasks from "./pages/Tasks";
import Architecture from "./pages/Architecture";
import Docs from "./pages/Docs";
import Playground from "./pages/Playground";
import NotFound from "./pages/NotFound";
import { AtomConnectionProvider } from "./lib/atomClient";

const App = () => (
  <BrowserRouter>
    <AtomConnectionProvider>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/environment" element={<Environment />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/architecture" element={<Architecture />} />
        <Route path="/docs" element={<Docs />} />
        <Route path="/playground" element={<Playground />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AtomConnectionProvider>
  </BrowserRouter>
);

export default App;

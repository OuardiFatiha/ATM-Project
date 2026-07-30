import { MapView } from './components/MapView'
import { Button } from 'primereact/button';
import { Toolbar } from 'primereact/toolbar';
import { RightPanel } from './components/RightPanel';
import { useState } from 'react';
import logo from './assets/logo.png';

function App() {
  const [visible, setVisible] = useState(false);
  const toolbarStart = <img alt="Flight Viewer" src={logo} height="40" style={{ display: 'block', mixBlendMode: 'multiply' }} />;
  const toolbarEnd = (
    <Button
      icon="pi pi-bars"
      onClick={() => setVisible(true)}
      severity="secondary"
      text
    />
  );

  return (
    <div
      className="App"
      style={{ width: '100%', height: '100%', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
    >
      <Toolbar start={toolbarStart} end={toolbarEnd} style={{ padding: '4px 12px', height: '80px' }} />
      <RightPanel visible={visible} setVisible={setVisible} />
      <MapView />
    </div>
  )
}

export default App

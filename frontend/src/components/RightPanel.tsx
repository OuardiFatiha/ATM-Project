import { Sidebar } from 'primereact/sidebar';
import { useAircraftStates } from '../hooks/useAircraftStates';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';

interface RightPanelProps {
    visible: boolean;
    setVisible: (visible: boolean) => void;
}

export const RightPanel = ({ visible, setVisible }: RightPanelProps) => {
    const { aircraftStates } = useAircraftStates();

    return (
        <Sidebar visible={visible} onHide={() => setVisible(false)} position="right" style={{ width: '500px' }}>
            <DataTable value={aircraftStates} paginator rows={10}>
                <Column field="callsign" header="Callsign" sortable></Column>
                <Column field="origin_country" header="Origin Country" sortable></Column>
                <Column field="barometric_altitude" header="Altitude" sortable></Column>
            </DataTable>
        </Sidebar>
    )
}
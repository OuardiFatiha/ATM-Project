import { Sidebar } from 'primereact/sidebar';
import { useConflicts } from '../hooks/useConflicts';
import { DataView } from 'primereact/dataview';
import type { Conflict } from '../types/Conflict';
import { Tag } from 'primereact/tag';
import { classNames } from 'primereact/utils';

interface RightPanelProps {
    visible: boolean;
    setVisible: (visible: boolean) => void;
}

export const RightPanel = ({ visible, setVisible }: RightPanelProps) => {
    const { conflicts: conflicts } = useConflicts();

    const sortedConflicts = [...conflicts].sort((a, b) => {
        const severityOrder =
            (a.severity === 'critical' ? 0 : 1) -
            (b.severity === 'critical' ? 0 : 1);

        return severityOrder || a.time_to_conflict_s - b.time_to_conflict_s;
    });

    const itemTemplate = (conflict: Conflict, index: number) => {
        return (
            <div className="col-12">
                <div className={classNames('flex flex-column xl:flex-row xl:align-items-start p-4 gap-4', { 'border-top-1 surface-border': index !== 0 })}>
                    <div className="flex flex-column sm:flex-row justify-content-between align-items-center xl:align-items-start flex-1 gap-4">
                        <div className="flex flex-column align-items-center sm:align-items-start gap-3">
                            <div>
                                <div className="text-2xl font-bold text-900">{conflict.callsign_1 ?? conflict.icao24_1}</div>
                                {conflict.callsign_1 && <small>ICAO: {conflict.icao24_1}</small>}
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-900">{conflict.callsign_2 ?? conflict.icao24_2}</div>
                                {conflict.callsign_2 && <small>ICAO: {conflict.icao24_2}</small>}
                            </div>
                            <div className="flex align-items-center gap-3">
                                <span className="flex align-items-center gap-2">
                                    <i className="pi pi-clock"></i>
                                    <span className="font-semibold">{conflict.time_to_conflict_s} s</span>
                                </span>
                                <Tag value={conflict.severity.toUpperCase()} severity={conflict.severity == 'critical' ? 'danger' : 'warning'}></Tag>
                            </div>
                        </div>
                        <div className="flex sm:flex-column">
                            <span className="text-2xl font-semibold">{conflict.horizontal_dist_nm.toFixed(2)} nm</span>
                            <span className="text-2xl font-semibold">{conflict.vertical_dist_ft.toFixed(2)} ft</span>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const listTemplate = (items: Conflict[]) => {
        if (!items || items.length === 0) return null;

        const list = items.map((product, index) => {
            return itemTemplate(product, index);
        });

        return <div className="grid grid-nogutter">{list}</div>;
    };

    return (
        <Sidebar visible={visible} onHide={() => setVisible(false)} position="right" style={{ width: '500px' }}>
            <div className="card">
                <DataView value={sortedConflicts} listTemplate={listTemplate} />
            </div>
        </Sidebar>
    )
}

import { Sidebar } from 'primereact/sidebar';
import { DataView } from 'primereact/dataview';
import type { Conflict } from '../types/Conflict';
import { Tag } from 'primereact/tag';
import { classNames } from 'primereact/utils';
import { useLiveFeedContext } from '../context/LiveFeedContext';

interface RightPanelProps {
    visible: boolean;
    setVisible: (visible: boolean) => void;
}

export const RightPanel = ({ visible, setVisible }: RightPanelProps) => {
    const { liveSnapshot } = useLiveFeedContext();
    const conflicts = liveSnapshot?.conflicts ?? [];

    const sortedConflicts = [...conflicts].sort((a, b) => {
        const severityOrder =
            (a.severity === 'critical' ? 0 : 1) -
            (b.severity === 'critical' ? 0 : 1);

        return severityOrder || a.time_to_conflict_s - b.time_to_conflict_s;
    });

    const itemTemplate = (conflict: Conflict, index: number) => {
        return (
            <div className="col-12 justify-content-center">
                <div className={classNames('flex flex-row justify-content-center p-4 gap-4', { 'border-top-1 surface-border': index !== 0 })}>
                    <div className="flex flex-row sm:flex-column justify-content-between align-items-center xl:align-items-start flex-1 w-full gap-4">
                        <div className="flex flex-row align-items-center sm:align-items-start gap-3">
                            <div>
                                <div className="text-xm font-bold text-900">{conflict.callsign_1 ?? conflict.icao24_1}</div>
                                {conflict.callsign_1 && <small>ICAO: {conflict.icao24_1}</small>}
                            </div>
                            <i className="pi pi-arrows-h"></i>
                            <div>
                                <div className="text-xm font-bold text-900">{conflict.callsign_2 ?? conflict.icao24_2}</div>
                                {conflict.callsign_2 && <small>ICAO: {conflict.icao24_2}</small>}
                            </div>
                        </div>
                        <div className="flex flex-row justify-content-start sm:align-items-start gap-7">
                            <div className="flex flex-column gap-2">
                                <Tag value={conflict.severity.toUpperCase()} severity={conflict.severity == 'critical' ? 'danger' : 'warning'}></Tag>
                                <span className="flex gap-2">
                                    <i className="pi pi-clock"></i>
                                    <span className="font-semibold">{conflict.time_to_conflict_s} s</span>
                                </span>
                            </div>
                            <div className="flex sm:flex-column gap-2">
                                <span className="text-xm font-semibold">{conflict.horizontal_dist_nm.toFixed(2)} nm</span>
                                <span className="text-xm font-semibold">{conflict.vertical_dist_ft.toFixed(2)} ft</span>
                            </div>
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
        <Sidebar
            visible={visible}
            onHide={() => setVisible(false)}
            position="right"
            style={{ width: '400px' }}
            header="CONFLICT ALERTS"
        >
            <div className="card">
                <DataView value={sortedConflicts} listTemplate={listTemplate} />
            </div>
        </Sidebar>
    )
}

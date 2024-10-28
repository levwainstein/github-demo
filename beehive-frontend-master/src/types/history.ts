
export type Tab = {
    label: string;
    component: JSX.Element;
};

export interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

export interface BHRating {
    score: number;
    text: string;
    created: Date;
    subject: string;
}

export interface HistoryElement {
    project: string;
    created: Date;
    name: string;
    duration: number;
    description: string;
    ratings: BHRating[];
}

export interface HistoryTableProps {
    title: string;
    subtitle: string;
    allRows: HistoryElement[];
}

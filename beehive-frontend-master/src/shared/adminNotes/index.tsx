import { makeStyles } from '@material-ui/styles';
import {
    DataGrid,
    GridColumns,
    GridRowsProp,
    GridSortDirection,
    GridSortModel
} from '@mui/x-data-grid';
import { FunctionComponent, useState } from 'react';

type Props = Record<string, never>;

const columns: GridColumns = [
    { field: 'adminName', headerName: 'Admin Name', width: 120, headerAlign: 'center', align: 'center', headerClassName: 'super-app-theme--header', cellClassName: 'super-app-theme--cell' },
    { field: 'title', headerName: 'Title', width: 200, headerAlign: 'center', align: 'center', headerClassName: 'super-app-theme--header', cellClassName: 'super-app-theme--cell' },
    { field: 'date', headerName: 'Date', width: 130, headerAlign: 'center', align: 'center', headerClassName: 'super-app-theme--header', cellClassName: 'super-app-theme--cell' },
    { field: 'feedback', headerName: 'Feedback', width: 750, headerAlign: 'center', align: 'center', headerClassName: 'super-app-theme--header', cellClassName: 'super-app-theme--cell' }
];
  
const rows: GridRowsProp = [
    {
        id: 1,
        adminName: 'John Doe',
        title: 'Animate hand and allow swipe in last part of help page',
        date: '02/02/2022',
        feedback: 'Im going to write an amazing feedback on some king who once did a really good job. He liked to take care of everyone and write code on a very high level. He also paid attention to the details and did his job with full responsibility'
    },
    {
        id: 2,
        adminName: 'Michael Doe',
        title: 'Animate hand and allow swipe in last part of help page',
        date: '02/02/2022',
        feedback: 'Im going to write an amazing feedback on some king who once did a really good job. He liked to take care of everyone and write code on a very high level. He also paid attention to the details and did his job with full responsibility'
    },
    {
        id: 3,
        adminName: 'Elizabeth',
        title: 'Animate hand and allow swipe in last part of help page',
        date: '02/02/2021',
        feedback: 'Im going to write an amazing feedback on some king who once did a really good job. He liked to take care of everyone and write code on a very high level. He also paid attention to the details and did his job with full responsibility'
    },
    {
        id: 4,
        adminName: 'Micky',
        title: 'Animate hand and allow swipe in last part of help page',
        date: '02/02/2022',
        feedback: 'Im going to write an amazing feedback on some king who once did a really good job. He liked to take care of everyone and write code on a very high level. He also paid attention to the details and did his job with full responsibility'
    }
];

const useStyles = makeStyles({
    root: {
        width: '100%',
        height: 450,
        '& .super-app-theme--header': {
            color: 'rgba(255, 255, 255, 0.9)',
            fontWeight: '500',
            fontSize: 12,
            border: 'none !important'
        },
        '& .MuiDataGrid-main': {
            borderBottom: 'none'
        },
        '& .MuiDataGrid-columnSeparator': {
            visibility: 'hidden'
        },
        '& .MuiDataGrid-columnHeaders': {
            borderBottom: '0.5px solid rgba(255, 255, 255, 0.25)'
        },
        '& div div div div >.MuiDataGrid-cell': {
            borderBottom: '0.5px solid rgba(255, 255, 255, 0.07);'
        },
        '& .MuiDataGrid-footerContainer': {
            border: 'none'
        },
        '& .MuiTablePagination-root': {
            color: 'rgba(255, 255, 255, 0.6)'
        },
        '& .MuiSvgIcon-root': {
            color: 'rgba(255, 255, 255, 0.6)'
        },
        '& .super-app-theme--cell': {
            color: '#ffffff99',
            fontWeight: '400',
            fontSize: 12,
            whiteSpace: 'normal !important'
        }
    }
});

const AdminNotes: FunctionComponent<Props> = () => {   
    const [ pageSize, setPageSize ] = useState<number>(5);
    const [ sortModel, setSortModel ] = useState<GridSortModel>([
        {
            field: 'date',
            sort: 'desc' as GridSortDirection
        }
    ]); 
    const classes = useStyles();

    return (
        <div className={classes.root}>
            <DataGrid
                pageSize={pageSize}
                onPageSizeChange={(newPageSize) => setPageSize(newPageSize)}
                rowsPerPageOptions={[ 5, 10, 20 ]}
                pagination
                sortModel={sortModel}
                rows={rows}
                columns={columns}
                onSortModelChange={(model) => setSortModel(model)}
                sx={{
                    backgroundColor: '#1E202A'
                }}
                rowHeight={85}
            />
        </div>
    );
};

export default AdminNotes;

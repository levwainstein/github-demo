import { makeStyles } from '@material-ui/core/styles';

export const useStyles = makeStyles(() => ({
    root: {
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#111218',
        '& .work-in-progress-btn': {
            backgroundColor: 'rgba(255, 220, 168, 0.1)',
            borderRadius: '100px',
            display: 'flex',
            justifyContent: 'space-around',
            alignItems: 'center',
            width: '250px',
            height: '40px',
            marginLeft: '140px'
        },
        '& .questions-btn': {
            backgroundColor: 'rgba(255, 220, 168, 0.1)',
            borderRadius: '100px',
            display: 'flex',
            justifyContent: 'space-around',
            alignItems: 'center',
            width: '250px',
            height: '40px',
            marginLeft: '147px'
        }
    },
    titleContainer: {
        display: 'flex',
        alignItems: 'center'
    },
    title: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 600,
        fontSize: '16px',
        lineHeight: '19.36px',
        color: 'rgba(255, 255, 255, 0.9)',
        marginLeft: 20
    },
    workInProgressText: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 700,
        fontSize: '12px',
        lineHeight: '12px',
        color: 'rgba(255, 255, 255, 0.6)'
    },
    cancelText: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 400,
        fontSize: '12px',
        lineHeight: '12px',
        color: 'rgba(250, 187, 24, 0.6)'
    },
    questionsText: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 400,
        fontSize: '12px',
        lineHeight: '23px',
        color: 'rgba(250, 187, 24, 0.8)'
    }
}));

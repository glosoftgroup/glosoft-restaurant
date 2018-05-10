export const TERM_SELECTED = 'TERM_SELECTED'

export const selectTerm = (payload) => {
    return {
        type: TERM_SELECTED,
        payload
    }
};
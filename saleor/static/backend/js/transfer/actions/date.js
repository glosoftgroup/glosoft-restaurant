export const DATE_SELECTED = 'DATE_SELECTED'

export const selectDate = (payload) => {
    return {
        type: DATE_SELECTED,
        payload
    }
};
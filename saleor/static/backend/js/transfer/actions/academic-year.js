export const ACADEMIC_YEAR_SELECTED = 'ACADEMIC_YEAR_SELECTED'

export const selectAcademicYear = (payload) => {
    return {
        type: ACADEMIC_YEAR_SELECTED,
        payload
    }
};
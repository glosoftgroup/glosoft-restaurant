export const COURSE_SELECTED = 'COURSE_SELECTED'

export const selectCourse = (payload) => {
    return {
        type: COURSE_SELECTED,
        payload
    }
};
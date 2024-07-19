export const wait = (time = 500) => new Promise((set) => setTimeout(set, time));

export const getFolder = (path: string) => {
    const paths = path.split("/");
    const folder = paths.slice(paths.length - 2).join("/");
    return folder;
} 

export const getSubmitFile = (path: string) => {
    const paths = path.split("/");
    const foldername = paths[2];
    const frame_idx = parseInt(paths[3]);
    const submission = foldername + ',' + frame_idx.toString()
    return submission;
} 

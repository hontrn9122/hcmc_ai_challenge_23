import { FC, createContext, useContext, useState } from "react";
import { ImageType } from "../types";
import { notification } from "antd";
import { getSubmitFile } from "../utils";

type SubmissionContextProps = {
  addSubmission: (image: ImageType) => void;
  removeSubmission: (id: string) => void;
  clearSubmission: () => void;
  downloadSubmission: () => void;
  submissions: ImageType[];
};

export const SubmissionContext = createContext({} as SubmissionContextProps);

export const useSubmission = () => useContext(SubmissionContext);

type SubmissionProviderProps = {
  children?: React.ReactNode;
};

export const SubmissionProvider: FC<SubmissionProviderProps> = ({ children }) => {
  const [submissions, setSubmissions] = useState<ImageType[]>([]);

  const addSubmission = (image: ImageType) => {
    if (!submissions.find((submission) => submission.path === image.path)) {
      setSubmissions((prev) => [...prev, image]);
      notification.success({ message: `Added submission: ${image.path}`, duration: 1 });
    } else {
      notification.warning({ message: "Submission already added", duration: 1 });
    }
  };

  const removeSubmission = (path: string) => {
    setSubmissions((prev) => prev.filter((image) => image.path !== path));
  };

  const clearSubmission = () => {
    setSubmissions([]);
  };

  // format path csv here ({ path }) => getFolder(path)
  const downloadSubmission = () => {
    const data = submissions.map(({ path }) => getSubmitFile(path)).join("\n");
    const csv = "data:text/csv;charset=utf-8," + data;
    const uri = encodeURI(csv);
    const anchor = document.createElement("a");
    anchor.download = "submission.csv";
    anchor.href = uri;
    anchor.click();
    anchor.remove();
  };

  return (
    <SubmissionContext.Provider
      value={{
        submissions,
        addSubmission,
        removeSubmission,
        clearSubmission,
        downloadSubmission,
      }}
    >
      {children}
    </SubmissionContext.Provider>
  );
};

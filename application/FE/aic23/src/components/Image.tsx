import { ImageType } from "../types";
import { FC, useEffect, useRef, useState } from "react";
import { getFolder } from "../utils";

type ImageProps = {
  image: ImageType;
  setId?: React.Dispatch<React.SetStateAction<string>>;
  action?: React.ReactNode;
};

const Image: FC<ImageProps> = ({ image, setId, action }) => {
  const { path } = image;
  const [preview, setPreview] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        setPreview(false);
      }
    };

    window.addEventListener("keydown", onEscape);

    return () => {
      window.removeEventListener("keydown", onEscape);
    };
  }, []);

  return (
    <>
      <div
        className="rounded-md overflow-hidden relative group shadow cursor-pointer"
        onClick={() => (setId ? setId(path) : setPreview(true))}
        ref={ref}
      >
        <img
          loading="lazy"
          src={`http://localhost:8000/images/${path}`}
          className="object-center object-cover w-full aspect-video h-full"
        />
        <div className="absolute opacity-0 group-hover:opacity-100 bg-black/30 h-full w-full top-0 left-0 transition-opacity flex items-end justify-end p-2">
          {action}
        </div>
        <div className="absolute top-0 px-3 py-2 text-sm text-ellipsis max-w-full overflow-hidden bg-black/20 text-white w-full">
          {getFolder(path)}
        </div>
      </div>
      {preview && (
        <div
          className="fixed top-0 left-0 z-[10000] bg-black/30 w-screen h-screen flex items-center justify-center"
          onClick={() => {
            setPreview(false);
          }}
        >
          <img
            className="h-[95%] object-center"
            src={`http://localhost:8000/images/${path}`}
          />
        </div>
      )}
    </>
  );
};

export default Image;

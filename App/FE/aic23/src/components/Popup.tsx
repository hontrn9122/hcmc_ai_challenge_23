import { Button, Empty, Spin } from "antd";
import { default as Image } from "./Image";
import { FC, useEffect, useRef, useState } from "react";
import { ImageType } from "../types";
import { useSubmission } from "../context";
import axiosClient from "../utils/axios";
import { getFolder } from "../utils";
import ReactPlayer from "react-player";

type PopupProps = {
  setId: React.Dispatch<React.SetStateAction<string>>;
  activePath: string;
};

const STEP = 12;

const Popup: FC<PopupProps> = ({ setId, activePath }) => {
  const { addSubmission } = useSubmission();
  const [images, setImages] = useState<ImageType[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const ref = useRef<ReactPlayer>(null);
  const [time, setTime] = useState({frame_idx: 0, second: 0});

  const activeImage = images.find((image) => image.path === activePath) || {
    path: "",
  };

  const maxPage = Math.ceil(images.length / STEP);

  console.log(time);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        setLoading(true);
        const paths = activePath.split("/");
        const folder = paths[paths.length - 2];
        const { data: {second, frame_idx} } = await axiosClient.post("/frameindex", {
          query : activePath,
        });

        const { data } = await axiosClient.post<ImageType[]>("/filename", {
          query: folder,
        });
        const images = data;
        const activeIndex = Math.max(
          0,
          images.findIndex((image) => image.path === activePath)
        );
        const currentPage = Math.floor(activeIndex / STEP);
        setPage(currentPage);
        setImages(images);
        setTime({frame_idx, second});
        ref.current?.seekTo(second);
      } catch (error) {
        console.log(error);
      } finally {
        setLoading(false);
      }
    };
    fetchImages();
  }, [activePath]);

  const onNext = () => {
    setPage((prev) => Math.min(maxPage, prev + 1));
  };

  const onBack = () => {
    setPage((prev) => Math.max(0, prev - 1));
  };

  const videoPath = getFolder(activePath).split("/")[0];
  const videoFolder = videoPath.split("_")[0];

  return (
    <div
      className="fixed top-0 left-0 w-screen h-screen bg-black/30 flex items-center justify-center z-[1000]"
      onClick={() => {
        setId("");
      }}
    >
      <div
        className="bg-white w-[95vw] h-[95vh] rounded-md flex p-4 gap-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex flex-col flex-1 gap-4">
          <div className="grid grid-cols-4 gap-4 grid-rows-3 flex-1">
            {loading ? (
              <Spin className="col-span-5 row-span-3 flex items-center justify-center" />
            ) : images.length === 0 ? (
              <Empty className="col-span-5 flex items-center flex-col justify-center" />
            ) : (
              images.slice(page * STEP, STEP * (page + 1)).map((image) => (
                <Image
                  key={image.path}
                  image={image}
                  setId={setId}
                  action={
                    <Button
                      type="primary"
                      onClick={(e) => {
                        e.stopPropagation();
                        addSubmission(image);
                      }}
                    >
                      Add
                    </Button>
                  }
                />
              ))
            )}
          </div>
          <div className="text-center flex justify-center mt-full items-center gap-4">
            <Button
              disabled={page === 0 || loading}
              className="my-auto h-full"
              type="primary"
              onClick={onBack}
            >
              &lt;
            </Button>
            {page + 1}/{maxPage}
            <Button
              disabled={page === maxPage - 1 || loading}
              className="my-auto h-full"
              type="primary"
              onClick={onNext}
            >
              &gt;
            </Button>
          </div>
        </div>
        {activeImage && (
          <div className="border-solid border-l-[1px] border-black/10 pl-4 w-1/4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-bold text-lg">Active image</h2>
              <Button
                type="primary"
                danger
                className="flex items-center justify-center"
                onClick={() => setId("")}
              >
                x
              </Button>
            </div>
            <Image image={activeImage} />
            <div className="mt-5"></div>
            <ReactPlayer
              ref={ref}
              url={`http://localhost:8000/videos/${videoFolder}/${videoPath}`}
              width={"100%"}
              height={"auto"}
              controls
              playing
              muted
            />
            <div className="font-bold mt-4 text-lg">
              Path: {getFolder(activePath)}
            </div>
            <div className="font-bold mt-4 text-lg">
              Frame index: {time.frame_idx}
            </div>
            <div className="font-bold mt-4 text-lg">
              Seconds: {time.second}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Popup;

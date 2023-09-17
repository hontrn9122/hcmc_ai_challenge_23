import { Header, Image, Popup } from "./components";
import { useState } from "react";
import { ImageType } from "./types";
import { Button, Empty, Spin } from "antd";
import { useSubmission } from "./context";

function App() {
  const [images, setImages] = useState<ImageType[]>([]);
  const [id, setId] = useState("");
  const { addSubmission } = useSubmission();
  const [loading, setLoading] = useState(false);

  return (
    <>
      <div className="flex">
        <Header loading={loading} setLoading={setLoading} setImages={setImages} images={images} />
        <div className="grid-cols-5 grid gap-4 p-4 flex-1">
          {loading ? (
            <Spin className="col-span-5 mt-40" />
          ) : images.length === 0 ? (
            <Empty className="col-span-5 mt-40" />
          ) : (
            images.map((image) => (
              <Image
                setId={setId}
                key={image.path}
                image={image}
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
      </div>
      {id ? <Popup activePath={id} setId={setId} /> : null}
    </>
  );
}

export default App;

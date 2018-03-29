FROM alpine
MAINTAINER Christian Roth <christian.roth@mpibpc.mpg.de>

ENV PENG_VERSION=1.0.0

RUN apk add --update wget g++ cmake boost-dev make
RUN wget https://github.com/soedinglab/PEnG-motif/archive/${PENG_VERSION}.tar.gz
RUN tar xzf ${PENG_VERSION}.tar.gz
RUN mkdir build
WORKDIR build
RUN cmake ../PEnG-motif-${PENG_VERSION} -DCMAKE_INSTALL_PREFIX=/bamm
RUN make -j4 install

RUN wget https://github.com/soedinglab/BaMMmotif2/archive/v2.0.tar.gz
RUN tar xzf v2.0.tar.gz
RUN mkdir build_bamm
WORKDIR build_bamm
RUN cmake ../BaMMmotif2-2.0 -DCMAKE_INSTALL_PREFIX=/bamm
RUN make -j4 install


FROM alpine
RUN apk add --update python3-dev python3 boost R-dev R gcc libgcc libc-dev
RUN R -e 'install.packages(c("argparse", "zoo", "fdrtool", "LSD"), repos="http://cran.us.r-project.org")'
RUN python3 -m pip install numpy

COPY --from=0 /bamm /bamm
RUN ln -s /usr/bin/python3 /bamm/bin/python
RUN chmod -R +rx /bamm/bin
ENV PATH "$PATH:/bamm/bin"
WORKDIR /data

#include <iostream>
#include <grpc++/grpc++.h>

#include "test.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using test::Greeter;
using test::HelloReply;
using test::HelloRequest;
using test::NumberReply;
using test::NumberRequest;

class GreeterServiceImpl final : public Greeter::Service {
    Status SayHello(ServerContext *context, const HelloRequest *request,
                    HelloReply *reply) override {
        std::string prefix("Hello, ");
        std::cout << "Received SayHello request: " << request->name()
                  << std::endl;
        reply->set_message(prefix + request->name());
        return Status::OK;
    }
    Status StreamNumbers(ServerContext *context, const NumberRequest *request,
                         grpc::ServerWriter<NumberReply> *writer) override {
        std::cout << "Received StreamNumbers request" << std::endl;
        for (int i = 0; i < request->count(); i++) {
            NumberReply reply;
            reply.set_number(i);
            std::cout << "Sending number " << i << std::endl;
            if (!writer->Write(reply)) {
                std::cout << "Client disconnected" << std::endl;
                break;
            }
        }
        return Status::OK;
    }
};

void RunServer() {
    std::string server_address("0.0.0.0:50051");
    GreeterServiceImpl service;

    ServerBuilder builder;
    // Listen on the given address without any authentication mechanism.
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    // Register "service" as the instance through which we'll communicate with
    // clients. In this case it corresponds to an *synchronous* service.
    builder.RegisterService(&service);
    // Finally assemble the server.
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Server listening on " << server_address << std::endl;

    // Wait for the server to shutdown. Note that some other thread must be
    // responsible for shutting down the server for this call to ever return.
    server->Wait();
}

int main(int argc, char **argv) {
    RunServer();
    return 0;
}

#include <OVR_CAPI.h>
#include <stdio.h>
#include <string>
#include <Windows.h>
#include <iostream>
#include <cstdlib>


int main()
{
	ovrInitParams initParams = { ovrInit_RequestVersion + ovrInit_Invisible, OVR_MINOR_VERSION, NULL, 0, 0 };
	ovrResult result = ovr_Initialize(&initParams);
	if (OVR_FAILURE(result))
		return 1;

	ovrSession session;
	ovrGraphicsLuid luid;
	result = ovr_Create(&session, &luid);
	if (OVR_FAILURE(result))
	{
		ovr_Shutdown();
		return 1;
	}

	ovrHmdDesc desc = ovr_GetHmdDesc(session);
	ovrInputState InputState;

	printf("Executing python script...\n");

	// Specify the Python script to execute
	char currentDir[MAX_PATH];
	GetCurrentDirectory(MAX_PATH, currentDir);
	printf(currentDir);
	const char* pythonScript = "\\..\\Scripts\\main.py";

	// Execute Python script using system command
	std::string command = "start cmd /k python3 " + std::string(currentDir) + std::string(pythonScript);
	if (system(command.c_str()) != 0) {
		std::cerr << "Error executing Python script" << std::endl;
		return 1;
	}

	printf("Creating named pipe...\n");

	// Create named pipe
	LPCSTR pipeName = "\\\\.\\pipe\\MyPipe";
	HANDLE hPipe = CreateNamedPipe(
		pipeName,
		PIPE_ACCESS_OUTBOUND,
		PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT,
		1,
		0,
		0,
		0,
		NULL
	);

	if (hPipe == INVALID_HANDLE_VALUE) {
		std::cerr << "Error creating named pipe: " << GetLastError() << std::endl;
		return 1;
	}

	// Connect to the named pipe
	if (ConnectNamedPipe(hPipe, NULL) == FALSE) {
		std::cerr << "Error connecting to named pipe: " << GetLastError() << std::endl;
		CloseHandle(hPipe);
		return 1;
	}

	while (1)
	{
		// Query the HMD for ts current tracking state.
		ovrTrackingState ts = ovr_GetTrackingState(session, ovr_GetTimeInSeconds(), ovrTrue);
		ovr_GetInputState(session, ovrControllerType_Touch, &InputState);
		ovrVector2f rightStick = InputState.Thumbstick[ovrHand_Right];
		ovrVector2f leftStick = InputState.Thumbstick[ovrHand_Left];
		const float radialDeadZone = 0.5;
		if (std::abs(rightStick.x) < radialDeadZone) rightStick.x = 0.0;
		if (std::abs(rightStick.y) < radialDeadZone) rightStick.y = 0.0;

		printf(
			" Touch Lin Vel (XY): %4.2f  %4.2f\n"
			" Touch Rot Vel (Z):  %4.2f\n",
			" HMD Ang Vel (YPR): %4.2f  %4.2f  %4.2f\n",
			rightStick.y, rightStick.x,
			leftStick.x,
			ts.HeadPose.AngularVelocity.y, -ts.HeadPose.AngularVelocity.x, -ts.HeadPose.AngularVelocity.z);

		// Send float data
		float data[] = {ts.HeadPose.AngularVelocity.y, -ts.HeadPose.AngularVelocity.x, -ts.HeadPose.AngularVelocity.z, rightStick.y, rightStick.x, leftStick.x};

		DWORD bytesWritten;
		if (WriteFile(hPipe, data, sizeof(data), &bytesWritten, NULL) == FALSE) {
			std::wcerr << "Error writing to named pipe: " << GetLastError() << std::endl;
		}
	}
	// Close the pipe
	CloseHandle(hPipe);

	ovr_Destroy(session);
	ovr_Shutdown();

	return 0;
}
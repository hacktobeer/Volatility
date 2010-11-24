# Volatility
# Copyright (C) 2008 Volatile Systems
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details. 
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA 
#

"""
@author:       AAron Walters and Brendan Dolan-Gavitt
@license:      GNU General Public License 2.0 or later
@contact:      awalters@volatilesystems.com,bdolangavitt@wesleyan.edu
@organization: Volatile Systems
"""

from operator import itemgetter
from bisect import bisect_right

import volatility.obj as obj
import volatility.win32.tasks as tasks
import volatility.win32.modules as modules
import volatility.commands as commands
import volatility.utils as utils
import volatility.debug as debug #pylint: disable-msg=W0611
from volatility.cache import CacheDecorator

#pylint: disable-msg=C0111

ssdt_types = {
  '_SERVICE_DESCRIPTOR_TABLE' : [ 0x40, {
    'Descriptors' : [0x0, ['array', 4, ['_SERVICE_DESCRIPTOR_ENTRY']]],
} ],
  '_SERVICE_DESCRIPTOR_ENTRY' : [ 0x10, {
    'KiServiceTable' : [0x0, ['pointer', ['void']]],
    'CounterBaseTable' : [0x4, ['pointer', ['unsigned long']]],
    'ServiceLimit' : [0x8, ['long']],
    'ArgumentTable' : [0xc, ['pointer', ['unsigned char']]],
} ],
}

# Derived using:
#   dps nt!KiServiceTable L 11c
#   dps win32k!W32pServiceTable L 29b
xpsp2_syscalls = [
    [   # Main syscall table
        'NtAcceptConnectPort',
        'NtAccessCheck',
        'NtAccessCheckAndAuditAlarm',
        'NtAccessCheckByType',
        'NtAccessCheckByTypeAndAuditAlarm',
        'NtAccessCheckByTypeResultList',
        'NtAccessCheckByTypeResultListAndAuditAlarm',
        'NtAccessCheckByTypeResultListAndAuditAlarmByHandle',
        'NtAddAtom',
        'NtAddBootEntry',
        'NtAdjustGroupsToken',
        'NtAdjustPrivilegesToken',
        'NtAlertResumeThread',
        'NtAlertThread',
        'NtAllocateLocallyUniqueId',
        'NtAllocateUserPhysicalPages',
        'NtAllocateUuids',
        'NtAllocateVirtualMemory',
        'NtAreMappedFilesTheSame',
        'NtAssignProcessToJobObject',
        'NtCallbackReturn',
        'NtCancelDeviceWakeupRequest',
        'NtCancelIoFile',
        'NtCancelTimer',
        'NtClearEvent',
        'NtClose',
        'NtCloseObjectAuditAlarm',
        'NtCompactKeys',
        'NtCompareTokens',
        'NtCompleteConnectPort',
        'NtCompressKey',
        'NtConnectPort',
        'NtContinue',
        'NtCreateDebugObject',
        'NtCreateDirectoryObject',
        'NtCreateEvent',
        'NtCreateEventPair',
        'NtCreateFile',
        'NtCreateIoCompletion',
        'NtCreateJobObject',
        'NtCreateJobSet',
        'NtCreateKey',
        'NtCreateMailslotFile',
        'NtCreateMutant',
        'NtCreateNamedPipeFile',
        'NtCreatePagingFile',
        'NtCreatePort',
        'NtCreateProcess',
        'NtCreateProcessEx',
        'NtCreateProfile',
        'NtCreateSection',
        'NtCreateSemaphore',
        'NtCreateSymbolicLinkObject',
        'NtCreateThread',
        'NtCreateTimer',
        'NtCreateToken',
        'NtCreateWaitablePort',
        'NtDebugActiveProcess',
        'NtDebugContinue',
        'NtDelayExecution',
        'NtDeleteAtom',
        'NtCancelDeviceWakeupRequest',
        'NtDeleteFile',
        'NtDeleteKey',
        'NtDeleteObjectAuditAlarm',
        'NtDeleteValueKey',
        'NtDeviceIoControlFile',
        'NtDisplayString',
        'NtDuplicateObject',
        'NtDuplicateToken',
        'NtAddBootEntry',
        'NtEnumerateKey',
        'NtEnumerateSystemEnvironmentValuesEx',
        'NtEnumerateValueKey',
        'NtExtendSection',
        'NtFilterToken',
        'NtFindAtom',
        'NtFlushBuffersFile',
        'NtFlushInstructionCache',
        'NtFlushKey',
        'NtFlushVirtualMemory',
        'NtFlushWriteBuffer',
        'NtFreeUserPhysicalPages',
        'NtFreeVirtualMemory',
        'NtFsControlFile',
        'NtGetContextThread',
        'NtGetDevicePowerState',
        'NtGetPlugPlayEvent',
        'NtGetWriteWatch',
        'NtImpersonateAnonymousToken',
        'NtImpersonateClientOfPort',
        'NtImpersonateThread',
        'NtInitializeRegistry',
        'NtInitiatePowerAction',
        'NtIsProcessInJob',
        'NtIsSystemResumeAutomatic',
        'NtListenPort',
        'NtLoadDriver',
        'NtLoadKey',
        'NtLoadKey2',
        'NtLockFile',
        'NtLockProductActivationKeys',
        'NtLockRegistryKey',
        'NtLockVirtualMemory',
        'NtMakePermanentObject',
        'NtMakeTemporaryObject',
        'NtMapUserPhysicalPages',
        'NtMapUserPhysicalPagesScatter',
        'NtMapViewOfSection',
        'NtCancelDeviceWakeupRequest',
        'NtNotifyChangeDirectoryFile',
        'NtNotifyChangeKey',
        'NtNotifyChangeMultipleKeys',
        'NtOpenDirectoryObject',
        'NtOpenEvent',
        'NtOpenEventPair',
        'NtOpenFile',
        'NtOpenIoCompletion',
        'NtOpenJobObject',
        'NtOpenKey',
        'NtOpenMutant',
        'NtOpenObjectAuditAlarm',
        'NtOpenProcess',
        'NtOpenProcessToken',
        'NtOpenProcessTokenEx',
        'NtOpenSection',
        'NtOpenSemaphore',
        'NtOpenSymbolicLinkObject',
        'NtOpenThread',
        'NtOpenThreadToken',
        'NtOpenThreadTokenEx',
        'NtOpenTimer',
        'NtPlugPlayControl',
        'NtPowerInformation',
        'NtPrivilegeCheck',
        'NtPrivilegeObjectAuditAlarm',
        'NtPrivilegedServiceAuditAlarm',
        'NtProtectVirtualMemory',
        'NtPulseEvent',
        'NtQueryAttributesFile',
        'NtAddBootEntry',
        'NtAddBootEntry',
        'NtQueryDebugFilterState',
        'NtQueryDefaultLocale',
        'NtQueryDefaultUILanguage',
        'NtQueryDirectoryFile',
        'NtQueryDirectoryObject',
        'NtQueryEaFile',
        'NtQueryEvent',
        'NtQueryFullAttributesFile',
        'NtQueryInformationAtom',
        'NtQueryInformationFile',
        'NtQueryInformationJobObject',
        'NtQueryInformationPort',
        'NtQueryInformationProcess',
        'NtQueryInformationThread',
        'NtQueryInformationToken',
        'NtQueryInstallUILanguage',
        'NtQueryIntervalProfile',
        'NtQueryIoCompletion',
        'NtQueryKey',
        'NtQueryMultipleValueKey',
        'NtQueryMutant',
        'NtQueryObject',
        'NtQueryOpenSubKeys',
        'NtQueryPerformanceCounter',
        'NtQueryQuotaInformationFile',
        'NtQuerySection',
        'NtQuerySecurityObject',
        'NtQuerySemaphore',
        'NtQuerySymbolicLinkObject',
        'NtQuerySystemEnvironmentValue',
        'NtQuerySystemEnvironmentValueEx',
        'NtQuerySystemInformation',
        'NtQuerySystemTime',
        'NtQueryTimer',
        'NtQueryTimerResolution',
        'NtQueryValueKey',
        'NtQueryVirtualMemory',
        'NtQueryVolumeInformationFile',
        'NtQueueApcThread',
        'NtRaiseException',
        'NtRaiseHardError',
        'NtReadFile',
        'NtReadFileScatter',
        'NtReadRequestData',
        'NtReadVirtualMemory',
        'NtRegisterThreadTerminatePort',
        'NtReleaseMutant',
        'NtReleaseSemaphore',
        'NtRemoveIoCompletion',
        'NtRemoveProcessDebug',
        'NtRenameKey',
        'NtReplaceKey',
        'NtReplyPort',
        'NtReplyWaitReceivePort',
        'NtReplyWaitReceivePortEx',
        'NtReplyWaitReplyPort',
        'NtRequestDeviceWakeup',
        'NtRequestPort',
        'NtRequestWaitReplyPort',
        'NtRequestWakeupLatency',
        'NtResetEvent',
        'NtResetWriteWatch',
        'NtRestoreKey',
        'NtResumeProcess',
        'NtResumeThread',
        'NtSaveKey',
        'NtSaveKeyEx',
        'NtSaveMergedKeys',
        'NtSecureConnectPort',
        'NtAddBootEntry',
        'NtAddBootEntry',
        'NtSetContextThread',
        'NtSetDebugFilterState',
        'NtSetDefaultHardErrorPort',
        'NtSetDefaultLocale',
        'NtSetDefaultUILanguage',
        'NtSetEaFile',
        'NtSetEvent',
        'NtSetEventBoostPriority',
        'NtSetHighEventPair',
        'NtSetHighWaitLowEventPair',
        'NtSetInformationDebugObject',
        'NtSetInformationFile',
        'NtSetInformationJobObject',
        'NtSetInformationKey',
        'NtSetInformationObject',
        'NtSetInformationProcess',
        'NtSetInformationThread',
        'NtSetInformationToken',
        'NtSetIntervalProfile',
        'NtSetIoCompletion',
        'NtSetLdtEntries',
        'NtSetLowEventPair',
        'NtSetLowWaitHighEventPair',
        'NtSetQuotaInformationFile',
        'NtSetSecurityObject',
        'NtSetSystemEnvironmentValue',
        'NtQuerySystemEnvironmentValueEx',
        'NtSetSystemInformation',
        'NtSetSystemPowerState',
        'NtSetSystemTime',
        'NtSetThreadExecutionState',
        'NtSetTimer',
        'NtSetTimerResolution',
        'NtSetUuidSeed',
        'NtSetValueKey',
        'NtSetVolumeInformationFile',
        'NtShutdownSystem',
        'NtSignalAndWaitForSingleObject',
        'NtStartProfile',
        'NtStopProfile',
        'NtSuspendProcess',
        'NtSuspendThread',
        'NtSystemDebugControl',
        'NtTerminateJobObject',
        'NtTerminateProcess',
        'NtTerminateThread',
        'NtTestAlert',
        'NtTraceEvent',
        'NtTranslateFilePath',
        'NtUnloadDriver',
        'NtUnloadKey',
        'NtUnloadKeyEx',
        'NtUnlockFile',
        'NtUnlockVirtualMemory',
        'NtUnmapViewOfSection',
        'NtVdmControl',
        'NtWaitForDebugEvent',
        'NtWaitForMultipleObjects',
        'NtWaitForSingleObject',
        'NtWaitHighEventPair',
        'NtWaitLowEventPair',
        'NtWriteFile',
        'NtWriteFileGather',
        'NtWriteRequestData',
        'NtWriteVirtualMemory',
        'NtYieldExecution',
        'NtCreateKeyedEvent',
        'NtOpenKeyedEvent',
        'NtReleaseKeyedEvent',
        'NtWaitForKeyedEvent',
        'NtQueryPortInformationProcess',
    ],
    [
        'NtGdiAbortDoc',
        'NtGdiAbortPath',
        'NtGdiAddFontResourceW',
        'NtGdiAddRemoteFontToDC',
        'NtGdiAddFontMemResourceEx',
        'NtGdiRemoveMergeFont',
        'NtGdiAddRemoteMMInstanceToDC',
        'NtGdiAlphaBlend',
        'NtGdiAngleArc',
        'NtGdiAnyLinkedFonts',
        'NtGdiFontIsLinked',
        'NtGdiArcInternal',
        'NtGdiBeginPath',
        'NtGdiBitBlt',
        'NtGdiCancelDC',
        'NtGdiCheckBitmapBits',
        'NtGdiCloseFigure',
        'NtGdiClearBitmapAttributes',
        'NtGdiClearBrushAttributes',
        'NtGdiColorCorrectPalette',
        'NtGdiCombineRgn',
        'NtGdiCombineTransform',
        'NtGdiComputeXformCoefficients',
        'NtGdiConsoleTextOut',
        'NtGdiConvertMetafileRect',
        'NtGdiCreateBitmap',
        'NtGdiCreateClientObj',
        'NtGdiCreateColorSpace',
        'NtGdiCreateColorTransform',
        'NtGdiCreateCompatibleBitmap',
        'NtGdiCreateCompatibleDC',
        'NtGdiCreateDIBBrush',
        'NtGdiCreateDIBitmapInternal',
        'NtGdiCreateDIBSection',
        'NtGdiCreateEllipticRgn',
        'NtGdiCreateHalftonePalette',
        'NtGdiCreateHatchBrushInternal',
        'NtGdiCreateMetafileDC',
        'NtGdiCreatePaletteInternal',
        'NtGdiCreatePatternBrushInternal',
        'NtGdiCreatePen',
        'NtGdiCreateRectRgn',
        'NtGdiCreateRoundRectRgn',
        'NtGdiCreateServerMetaFile',
        'NtGdiCreateSolidBrush',
        'NtGdiD3dContextCreate',
        'NtGdiD3dContextDestroy',
        'NtGdiD3dContextDestroyAll',
        'NtGdiD3dValidateTextureStageState',
        'NtGdiD3dDrawPrimitives2',
        'NtGdiDdGetDriverState',
        'NtGdiDdAddAttachedSurface',
        'NtGdiDdAlphaBlt',
        'NtGdiDdAttachSurface',
        'NtGdiDdBeginMoCompFrame',
        'NtGdiDdBlt',
        'NtGdiDdCanCreateSurface',
        'NtGdiDdCanCreateD3DBuffer',
        'NtGdiDdColorControl',
        'NtGdiDdCreateDirectDrawObject',
        'NtGdiDdCreateSurface',
        'NtGdiDdCreateD3DBuffer',
        'NtGdiDdCreateMoComp',
        'NtGdiDdCreateSurfaceObject',
        'NtGdiDdDeleteDirectDrawObject',
        'NtGdiDdDeleteSurfaceObject',
        'NtGdiDdDestroyMoComp',
        'NtGdiDdDestroySurface',
        'NtGdiDdDestroyD3DBuffer',
        'NtGdiDdEndMoCompFrame',
        'NtGdiDdFlip',
        'NtGdiDdFlipToGDISurface',
        'NtGdiDdGetAvailDriverMemory',
        'NtGdiDdGetBltStatus',
        'NtGdiDdGetDC',
        'NtGdiDdGetDriverInfo',
        'NtGdiDdGetDxHandle',
        'NtGdiDdGetFlipStatus',
        'NtGdiDdGetInternalMoCompInfo',
        'NtGdiDdGetMoCompBuffInfo',
        'NtGdiDdGetMoCompGuids',
        'NtGdiDdGetMoCompFormats',
        'NtGdiDdGetScanLine',
        'NtGdiDdLock',
        'NtGdiDdLockD3D',
        'NtGdiDdQueryDirectDrawObject',
        'NtGdiDdQueryMoCompStatus',
        'NtGdiDdReenableDirectDrawObject',
        'NtGdiDdReleaseDC',
        'NtGdiDdRenderMoComp',
        'NtGdiDdResetVisrgn',
        'NtGdiDdSetColorKey',
        'NtGdiDdSetExclusiveMode',
        'NtGdiDdSetGammaRamp',
        'NtGdiDdCreateSurfaceEx',
        'NtGdiDdSetOverlayPosition',
        'NtGdiDdUnattachSurface',
        'NtGdiDdUnlock',
        'NtGdiDdUnlockD3D',
        'NtGdiDdUpdateOverlay',
        'NtGdiDdWaitForVerticalBlank',
        'NtGdiDvpCanCreateVideoPort',
        'NtGdiDvpColorControl',
        'NtGdiDvpCreateVideoPort',
        'NtGdiDvpDestroyVideoPort',
        'NtGdiDvpFlipVideoPort',
        'NtGdiDvpGetVideoPortBandwidth',
        'NtGdiDvpGetVideoPortField',
        'NtGdiDvpGetVideoPortFlipStatus',
        'NtGdiDvpGetVideoPortInputFormats',
        'NtGdiDvpGetVideoPortLine',
        'NtGdiDvpGetVideoPortOutputFormats',
        'NtGdiDvpGetVideoPortConnectInfo',
        'NtGdiDvpGetVideoSignalStatus',
        'NtGdiDvpUpdateVideoPort',
        'NtGdiDvpWaitForVideoPortSync',
        'NtGdiDvpAcquireNotification',
        'NtGdiDvpReleaseNotification',
        'NtGdiDxgGenericThunk',
        'NtGdiDeleteClientObj',
        'NtGdiDeleteColorSpace',
        'NtGdiDeleteColorTransform',
        'NtGdiDeleteObjectApp',
        'NtGdiDescribePixelFormat',
        'NtGdiGetPerBandInfo',
        'NtGdiDoBanding',
        'NtGdiDoPalette',
        'NtGdiDrawEscape',
        'NtGdiEllipse',
        'NtGdiEnableEudc',
        'NtGdiEndDoc',
        'NtGdiEndPage',
        'NtGdiEndPath',
        'NtGdiEnumFontChunk',
        'NtGdiEnumFontClose',
        'NtGdiEnumFontOpen',
        'NtGdiEnumObjects',
        'NtGdiEqualRgn',
        'NtGdiEudcLoadUnloadLink',
        'NtGdiExcludeClipRect',
        'NtGdiExtCreatePen',
        'NtGdiExtCreateRegion',
        'NtGdiExtEscape',
        'NtGdiExtFloodFill',
        'NtGdiExtGetObjectW',
        'NtGdiExtSelectClipRgn',
        'NtGdiExtTextOutW',
        'NtGdiFillPath',
        'NtGdiFillRgn',
        'NtGdiFlattenPath',
        'NtGdiFlushUserBatch',
        'NtGdiFlush',
        'NtGdiForceUFIMapping',
        'NtGdiFrameRgn',
        'NtGdiFullscreenControl',
        'NtGdiGetAndSetDCDword',
        'NtGdiGetAppClipBox',
        'NtGdiGetBitmapBits',
        'NtGdiGetBitmapDimension',
        'NtGdiGetBoundsRect',
        'NtGdiGetCharABCWidthsW',
        'NtGdiGetCharacterPlacementW',
        'NtGdiGetCharSet',
        'NtGdiGetCharWidthW',
        'NtGdiGetCharWidthInfo',
        'NtGdiGetColorAdjustment',
        'NtGdiGetColorSpaceforBitmap',
        'NtGdiGetDCDword',
        'NtGdiGetDCforBitmap',
        'NtGdiGetDCObject',
        'NtGdiGetDCPoint',
        'NtGdiGetDeviceCaps',
        'NtGdiGetDeviceGammaRamp',
        'NtGdiGetDeviceCapsAll',
        'NtGdiGetDIBitsInternal',
        'NtGdiGetETM',
        'NtGdiGetEudcTimeStampEx',
        'NtGdiGetFontData',
        'NtGdiGetFontResourceInfoInternalW',
        'NtGdiGetGlyphIndicesW',
        'NtGdiGetGlyphIndicesWInternal',
        'NtGdiGetGlyphOutline',
        'NtGdiGetKerningPairs',
        'NtGdiGetLinkedUFIs',
        'NtGdiGetMiterLimit',
        'NtGdiGetMonitorID',
        'NtGdiGetNearestColor',
        'NtGdiGetNearestPaletteIndex',
        'NtGdiGetObjectBitmapHandle',
        'NtGdiGetOutlineTextMetricsInternalW',
        'NtGdiGetPath',
        'NtGdiGetPixel',
        'NtGdiGetRandomRgn',
        'NtGdiGetRasterizerCaps',
        'NtGdiGetRealizationInfo',
        'NtGdiGetRegionData',
        'NtGdiGetRgnBox',
        'NtGdiGetServerMetaFileBits',
        'NtGdiGetSpoolMessage',
        'NtGdiGetStats',
        'NtGdiGetStockObject',
        'NtGdiGetStringBitmapW',
        'NtGdiGetSystemPaletteUse',
        'NtGdiGetTextCharsetInfo',
        'NtGdiGetTextExtent',
        'NtGdiGetTextExtentExW',
        'NtGdiGetTextFaceW',
        'NtGdiGetTextMetricsW',
        'NtGdiGetTransform',
        'NtGdiGetUFI',
        'NtGdiGetEmbUFI',
        'NtGdiGetUFIPathname',
        'NtGdiGetEmbedFonts',
        'NtGdiChangeGhostFont',
        'NtGdiAddEmbFontToDC',
        'NtGdiGetFontUnicodeRanges',
        'NtGdiGetWidthTable',
        'NtGdiGradientFill',
        'NtGdiHfontCreate',
        'NtGdiIcmBrushInfo',
        'NtGdiInit',
        'NtGdiInitSpool',
        'NtGdiIntersectClipRect',
        'NtGdiInvertRgn',
        'NtGdiLineTo',
        'NtGdiMakeFontDir',
        'NtGdiMakeInfoDC',
        'NtGdiMaskBlt',
        'NtGdiModifyWorldTransform',
        'NtGdiMonoBitmap',
        'NtGdiMoveTo',
        'NtGdiOffsetClipRgn',
        'NtGdiOffsetRgn',
        'NtGdiOpenDCW',
        'NtGdiPatBlt',
        'NtGdiPolyPatBlt',
        'NtGdiPathToRegion',
        'NtGdiPlgBlt',
        'NtGdiPolyDraw',
        'NtGdiPolyPolyDraw',
        'NtGdiPolyTextOutW',
        'NtGdiPtInRegion',
        'NtGdiPtVisible',
        'NtGdiQueryFonts',
        'NtGdiQueryFontAssocInfo',
        'NtGdiRectangle',
        'NtGdiRectInRegion',
        'NtGdiRectVisible',
        'NtGdiRemoveFontResourceW',
        'NtGdiRemoveFontMemResourceEx',
        'NtGdiResetDC',
        'NtGdiResizePalette',
        'NtGdiRestoreDC',
        'NtGdiRoundRect',
        'NtGdiSaveDC',
        'NtGdiScaleViewportExtEx',
        'NtGdiScaleWindowExtEx',
        'GreSelectBitmap',
        'NtGdiSelectBrush',
        'NtGdiSelectClipPath',
        'NtGdiSelectFont',
        'NtGdiSelectPen',
        'NtGdiSetBitmapAttributes',
        'NtGdiSetBitmapBits',
        'NtGdiSetBitmapDimension',
        'NtGdiSetBoundsRect',
        'NtGdiSetBrushAttributes',
        'NtGdiSetBrushOrg',
        'NtGdiSetColorAdjustment',
        'NtGdiSetColorSpace',
        'NtGdiSetDeviceGammaRamp',
        'NtGdiSetDIBitsToDeviceInternal',
        'NtGdiSetFontEnumeration',
        'NtGdiSetFontXform',
        'NtGdiSetIcmMode',
        'NtGdiSetLinkedUFIs',
        'NtGdiSetMagicColors',
        'NtGdiSetMetaRgn',
        'NtGdiSetMiterLimit',
        'NtGdiGetDeviceWidth',
        'NtGdiMirrorWindowOrg',
        'NtGdiSetLayout',
        'NtGdiSetPixel',
        'NtGdiSetPixelFormat',
        'NtGdiSetRectRgn',
        'NtGdiSetSystemPaletteUse',
        'NtGdiSetTextJustification',
        'NtGdiSetupPublicCFONT',
        'NtGdiSetVirtualResolution',
        'NtGdiSetSizeDevice',
        'NtGdiStartDoc',
        'NtGdiStartPage',
        'NtGdiStretchBlt',
        'NtGdiStretchDIBitsInternal',
        'NtGdiStrokeAndFillPath',
        'NtGdiStrokePath',
        'NtGdiSwapBuffers',
        'NtGdiTransformPoints',
        'NtGdiTransparentBlt',
        'NtGdiUnloadPrinterDriver',
        'NtGdiUnmapMemFont',
        'NtGdiUnrealizeObject',
        'NtGdiUpdateColors',
        'NtGdiWidenPath',
        'NtUserActivateKeyboardLayout',
        'NtUserAlterWindowStyle',
        'NtUserAssociateInputContext',
        'NtUserAttachThreadInput',
        'NtUserBeginPaint',
        'NtUserBitBltSysBmp',
        'NtUserBlockInput',
        'NtUserBuildHimcList',
        'NtUserBuildHwndList',
        'NtUserBuildNameList',
        'NtUserBuildPropList',
        'NtUserCallHwnd',
        'NtUserCallHwndLock',
        'NtUserCallHwndOpt',
        'NtUserCallHwndParam',
        'NtUserCallHwndParamLock',
        'NtUserCallMsgFilter',
        'NtUserCallNextHookEx',
        'NtUserCallNoParam',
        'NtUserCallOneParam',
        'NtUserCallTwoParam',
        'NtUserChangeClipboardChain',
        'NtUserChangeDisplaySettings',
        'NtUserCheckImeHotKey',
        'NtUserCheckMenuItem',
        'NtUserChildWindowFromPointEx',
        'NtUserClipCursor',
        'NtUserCloseClipboard',
        'NtUserCloseDesktop',
        'NtUserCloseWindowStation',
        'NtUserConsoleControl',
        'NtUserConvertMemHandle',
        'NtUserCopyAcceleratorTable',
        'NtUserCountClipboardFormats',
        'NtUserCreateAcceleratorTable',
        'NtUserCreateCaret',
        'NtUserCreateDesktop',
        'NtUserCreateInputContext',
        'NtUserCreateLocalMemHandle',
        'NtUserCreateWindowEx',
        'NtUserCreateWindowStation',
        'NtUserDdeGetQualityOfService',
        'NtUserDdeInitialize',
        'NtUserDdeSetQualityOfService',
        'NtUserDeferWindowPos',
        'NtUserDefSetText',
        'NtUserDeleteMenu',
        'NtUserDestroyAcceleratorTable',
        'NtUserDestroyCursor',
        'NtUserDestroyInputContext',
        'NtUserDestroyMenu',
        'NtUserDestroyWindow',
        'NtUserDisableThreadIme',
        'NtUserDispatchMessage',
        'NtUserDragDetect',
        'NtUserDragObject',
        'NtUserDrawAnimatedRects',
        'NtUserDrawCaption',
        'NtUserDrawCaptionTemp',
        'NtUserDrawIconEx',
        'NtUserDrawMenuBarTemp',
        'NtUserEmptyClipboard',
        'NtUserEnableMenuItem',
        'NtUserEnableScrollBar',
        'NtUserEndDeferWindowPosEx',
        'NtUserEndMenu',
        'NtUserEndPaint',
        'NtUserEnumDisplayDevices',
        'NtUserEnumDisplayMonitors',
        'NtUserEnumDisplaySettings',
        'NtUserEvent',
        'NtUserExcludeUpdateRgn',
        'NtUserFillWindow',
        'NtUserFindExistingCursorIcon',
        'NtUserFindWindowEx',
        'NtUserFlashWindowEx',
        'NtUserGetAltTabInfo',
        'NtUserGetAncestor',
        'NtUserGetAppImeLevel',
        'NtUserGetAsyncKeyState',
        'NtUserGetAtomName',
        'NtUserGetCaretBlinkTime',
        'NtUserGetCaretPos',
        'NtUserGetClassInfo',
        'NtUserGetClassName',
        'NtUserGetClipboardData',
        'NtUserGetClipboardFormatName',
        'NtUserGetClipboardOwner',
        'NtUserGetClipboardSequenceNumber',
        'NtUserGetClipboardViewer',
        'NtUserGetClipCursor',
        'NtUserGetComboBoxInfo',
        'NtUserGetControlBrush',
        'NtUserGetControlColor',
        'NtUserGetCPD',
        'NtUserGetCursorFrameInfo',
        'NtUserGetCursorInfo',
        'NtUserGetDC',
        'NtUserGetDCEx',
        'NtUserGetDoubleClickTime',
        'NtUserGetForegroundWindow',
        'NtUserGetGuiResources',
        'NtUserGetGUIThreadInfo',
        'NtUserGetIconInfo',
        'NtUserGetIconSize',
        'NtUserGetImeHotKey',
        'NtUserGetImeInfoEx',
        'NtUserGetInternalWindowPos',
        'NtUserGetKeyboardLayoutList',
        'NtUserGetKeyboardLayoutName',
        'NtUserGetKeyboardState',
        'NtUserGetKeyNameText',
        'NtUserGetKeyState',
        'NtUserGetListBoxInfo',
        'NtUserGetMenuBarInfo',
        'NtUserGetMenuIndex',
        'NtUserGetMenuItemRect',
        'NtUserGetMessage',
        'NtUserGetMouseMovePointsEx',
        'NtUserGetObjectInformation',
        'NtUserGetOpenClipboardWindow',
        'NtUserGetPriorityClipboardFormat',
        'NtUserGetProcessWindowStation',
        'NtUserGetRawInputBuffer',
        'NtUserGetRawInputData',
        'NtUserGetRawInputDeviceInfo',
        'NtUserGetRawInputDeviceList',
        'NtUserGetRegisteredRawInputDevices',
        'NtUserGetScrollBarInfo',
        'NtUserGetSystemMenu',
        'NtUserGetThreadDesktop',
        'NtUserGetThreadState',
        'NtUserGetTitleBarInfo',
        'NtUserGetUpdateRect',
        'NtUserGetUpdateRgn',
        'NtUserGetWindowDC',
        'NtUserGetWindowPlacement',
        'NtUserGetWOWClass',
        'NtUserHardErrorControl',
        'NtUserHideCaret',
        'NtUserHiliteMenuItem',
        'NtUserImpersonateDdeClientWindow',
        'NtUserInitialize',
        'NtUserInitializeClientPfnArrays',
        'NtUserInitTask',
        'NtUserInternalGetWindowText',
        'NtUserInvalidateRect',
        'NtUserInvalidateRgn',
        'NtUserIsClipboardFormatAvailable',
        'NtUserKillTimer',
        'NtUserLoadKeyboardLayoutEx',
        'NtUserLockWindowStation',
        'NtUserLockWindowUpdate',
        'NtUserLockWorkStation',
        'NtUserMapVirtualKeyEx',
        'NtUserMenuItemFromPoint',
        'NtUserMessageCall',
        'NtUserMinMaximize',
        'NtUserMNDragLeave',
        'NtUserMNDragOver',
        'NtUserModifyUserStartupInfoFlags',
        'NtUserMoveWindow',
        'NtUserNotifyIMEStatus',
        'NtUserNotifyProcessCreate',
        'NtUserNotifyWinEvent',
        'NtUserOpenClipboard',
        'NtUserOpenDesktop',
        'NtUserOpenInputDesktop',
        'NtUserOpenWindowStation',
        'NtUserPaintDesktop',
        'NtUserPeekMessage',
        'NtUserPostMessage',
        'NtUserPostThreadMessage',
        'NtUserPrintWindow',
        'NtUserProcessConnect',
        'NtUserQueryInformationThread',
        'NtUserQueryInputContext',
        'NtUserQuerySendMessage',
        'NtUserQueryUserCounters',
        'NtUserQueryWindow',
        'NtUserRealChildWindowFromPoint',
        'NtUserRealInternalGetMessage',
        'NtUserRealWaitMessageEx',
        'NtUserRedrawWindow',
        'NtUserRegisterClassExWOW',
        'NtUserRegisterUserApiHook',
        'NtUserRegisterHotKey',
        'NtUserRegisterRawInputDevices',
        'NtUserRegisterTasklist',
        'NtUserRegisterWindowMessage',
        'NtUserRemoveMenu',
        'NtUserRemoveProp',
        'NtUserResolveDesktop',
        'NtUserResolveDesktopForWOW',
        'NtUserSBGetParms',
        'NtUserScrollDC',
        'NtUserScrollWindowEx',
        'NtUserSelectPalette',
        'NtUserSendInput',
        'NtUserSetActiveWindow',
        'NtUserSetAppImeLevel',
        'NtUserSetCapture',
        'NtUserSetClassLong',
        'NtUserSetClassWord',
        'NtUserSetClipboardData',
        'NtUserSetClipboardViewer',
        'NtUserSetConsoleReserveKeys',
        'NtUserSetCursor',
        'NtUserSetCursorContents',
        'NtUserSetCursorIconData',
        'NtUserSetDbgTag',
        'NtUserSetFocus',
        'NtUserSetImeHotKey',
        'NtUserSetImeInfoEx',
        'NtUserSetImeOwnerWindow',
        'NtUserSetInformationProcess',
        'NtUserSetInformationThread',
        'NtUserSetInternalWindowPos',
        'NtUserSetKeyboardState',
        'NtUserSetLogonNotifyWindow',
        'NtUserSetMenu',
        'NtUserSetMenuContextHelpId',
        'NtUserSetMenuDefaultItem',
        'NtUserSetMenuFlagRtoL',
        'NtUserSetObjectInformation',
        'NtUserSetParent',
        'NtUserSetProcessWindowStation',
        'NtUserSetProp',
        'NtUserSetRipFlags',
        'NtUserSetScrollInfo',
        'NtUserSetShellWindowEx',
        'NtUserSetSysColors',
        'NtUserSetSystemCursor',
        'NtUserSetSystemMenu',
        'NtUserSetSystemTimer',
        'NtUserSetThreadDesktop',
        'NtUserSetThreadLayoutHandles',
        'NtUserSetThreadState',
        'NtUserSetTimer',
        'NtUserSetWindowFNID',
        'NtUserSetWindowLong',
        'NtUserSetWindowPlacement',
        'NtUserSetWindowPos',
        'NtUserSetWindowRgn',
        'NtUserSetWindowsHookAW',
        'NtUserSetWindowsHookEx',
        'NtUserSetWindowStationUser',
        'NtUserSetWindowWord',
        'NtUserSetWinEventHook',
        'NtUserShowCaret',
        'NtUserShowScrollBar',
        'NtUserShowWindow',
        'NtUserShowWindowAsync',
        'NtUserSoundSentry',
        'NtUserSwitchDesktop',
        'NtUserSystemParametersInfo',
        'NtUserTestForInteractiveUser',
        'NtUserThunkedMenuInfo',
        'NtUserThunkedMenuItemInfo',
        'NtUserToUnicodeEx',
        'NtUserTrackMouseEvent',
        'NtUserTrackPopupMenuEx',
        'NtUserCalcMenuBar',
        'NtUserPaintMenuBar',
        'NtUserTranslateAccelerator',
        'NtUserTranslateMessage',
        'NtUserUnhookWindowsHookEx',
        'NtUserUnhookWinEvent',
        'NtUserUnloadKeyboardLayout',
        'NtUserUnlockWindowStation',
        'NtUserUnregisterClass',
        'NtUserUnregisterUserApiHook',
        'NtUserUnregisterHotKey',
        'NtUserUpdateInputContext',
        'NtUserUpdateInstance',
        'NtUserUpdateLayeredWindow',
        'NtUserGetLayeredWindowAttributes',
        'NtUserSetLayeredWindowAttributes',
        'NtUserUpdatePerUserSystemParameters',
        'NtUserUserHandleGrantAccess',
        'NtUserValidateHandleSecure',
        'NtUserValidateRect',
        'NtUserValidateTimerCallback',
        'NtUserVkKeyScanEx',
        'NtUserWaitForInputIdle',
        'NtUserWaitForMsgAndEvent',
        'NtUserWaitMessage',
        'NtUserWin32PoolAllocationStats',
        'NtUserWindowFromPoint',
        'NtUserYieldTask',
        'NtUserRemoteConnect',
        'NtUserRemoteRedrawRectangle',
        'NtUserRemoteRedrawScreen',
        'NtUserRemoteStopScreenUpdates',
        'NtUserCtxDisplayIOCtl',
        'NtGdiEngAssociateSurface',
        'NtGdiEngCreateBitmap',
        'NtGdiEngCreateDeviceSurface',
        'NtGdiEngCreateDeviceBitmap',
        'NtGdiEngCreatePalette',
        'NtGdiEngComputeGlyphSet',
        'NtGdiEngCopyBits',
        'NtGdiEngDeletePalette',
        'NtGdiEngDeleteSurface',
        'NtGdiEngEraseSurface',
        'NtGdiEngUnlockSurface',
        'NtGdiEngLockSurface',
        'NtGdiEngBitBlt',
        'NtGdiEngStretchBlt',
        'NtGdiEngPlgBlt',
        'NtGdiEngMarkBandingSurface',
        'NtGdiEngStrokePath',
        'NtGdiEngFillPath',
        'NtGdiEngStrokeAndFillPath',
        'NtGdiEngPaint',
        'NtGdiEngLineTo',
        'NtGdiEngAlphaBlend',
        'NtGdiEngGradientFill',
        'NtGdiEngTransparentBlt',
        'NtGdiEngTextOut',
        'NtGdiEngStretchBltROP',
        'NtGdiXLATEOBJ_cGetPalette',
        'NtGdiXLATEOBJ_iXlate',
        'NtGdiXLATEOBJ_hGetColorTransform',
        'NtGdiCLIPOBJ_bEnum',
        'NtGdiCLIPOBJ_cEnumStart',
        'NtGdiCLIPOBJ_ppoGetPath',
        'NtGdiEngDeletePath',
        'NtGdiEngCreateClip',
        'NtGdiEngDeleteClip',
        'NtGdiBRUSHOBJ_ulGetBrushColor',
        'NtGdiBRUSHOBJ_pvAllocRbrush',
        'NtGdiBRUSHOBJ_pvGetRbrush',
        'NtGdiBRUSHOBJ_hGetColorTransform',
        'NtGdiXFORMOBJ_bApplyXform',
        'NtGdiXFORMOBJ_iGetXform',
        'NtGdiFONTOBJ_vGetInfo',
        'NtGdiFONTOBJ_pxoGetXform',
        'NtGdiFONTOBJ_cGetGlyphs',
        'NtGdiFONTOBJ_pifi',
        'NtGdiFONTOBJ_pfdg',
        'NtGdiFONTOBJ_pQueryGlyphAttrs',
        'NtGdiFONTOBJ_pvTrueTypeFontFile',
        'NtGdiFONTOBJ_cGetAllGlyphHandles',
        'NtGdiSTROBJ_bEnum',
        'NtGdiSTROBJ_bEnumPositionsOnly',
        'NtGdiSTROBJ_bGetAdvanceWidths',
        'NtGdiSTROBJ_vEnumStart',
        'NtGdiSTROBJ_dwGetCodePage',
        'NtGdiPATHOBJ_vGetBounds',
        'NtGdiPATHOBJ_bEnum',
        'NtGdiPATHOBJ_vEnumStart',
        'NtGdiPATHOBJ_vEnumStartClipLines',
        'NtGdiPATHOBJ_bEnumClipLines',
        'NtGdiGetDhpdev',
        'NtGdiEngCheckAbort',
        'NtGdiHT_Get8BPPFormatPalette',
        'NtGdiHT_Get8BPPMaskPalette',
        'NtGdiUpdateTransform',
        'NtGdiSetPUMPDOBJ',
        'NtGdiBRUSHOBJ_DeleteRbrush',
        'NtGdiUnmapMemFont',
        'NtGdiDrawStream',
    ],
]

def find_module(modlist, mod_addrs, addr):
    """Uses binary search to find what module a given address resides in.

    This is much faster than a series of linear checks if you have
    to do it many times. Note that modlist and mod_addrs must be sorted
    in order of the module base address."""

    pos = bisect_right(mod_addrs, addr) - 1
    if pos == -1:
        return None
    mod = modlist[mod_addrs[pos]]

    if (addr >= mod.DllBase.v() and
        addr < mod.DllBase.v() + mod.SizeOfImage.v()):
        return mod
    else:
        return None

class SSDT(commands.command):
    "Display SSDT entries"
    # Declare meta information associated with this plugin
    meta_info = {
        'author': 'Brendan Dolan-Gavitt',
        'copyright': 'Copyright (c) 2007,2008 Brendan Dolan-Gavitt',
        'contact': 'bdolangavitt@wesleyan.edu',
        'license': 'GNU General Public License 2.0 or later',
        'url': 'http://moyix.blogspot.com/',
        'os': 'WIN_32_XP_SP2',
        'version': '1.0'}

    @CacheDecorator("tests/ssdt")
    def calculate(self):
        addr_space = utils.load_as(self._config)
        addr_space.profile.add_types(ssdt_types)

        ## Get a sorted list of module addresses
        mods = dict((mod.DllBase.v(), mod) for mod in modules.lsmod(addr_space))
        mod_addrs = sorted(mods.keys())

        # Gather up all SSDTs referenced by threads
        print "Gathering all referenced SSDTs from KTHREADs..."
        ssdts = set()
        for proc in tasks.pslist(addr_space):
            for thread in proc.ThreadListHead.list_of_type("_ETHREAD", "ThreadListEntry"):
                ssdt_obj = thread.Tcb.ServiceTable.dereference_as('_SERVICE_DESCRIPTOR_TABLE')
                ssdts.add(ssdt_obj)

        # Get a list of *unique* SSDT entries. Typically we see only two.
        tables = set()

        for ssdt_obj in ssdts:
            for i, desc in enumerate(ssdt_obj.Descriptors):
                # Apply some extra checks - KiServiceTable should reside in kernel memory and ServiceLimit 
                # should be greater than 0 but not unbelievably high
                if desc.is_valid() and desc.ServiceLimit > 0 and desc.ServiceLimit < 0xFFFF and desc.KiServiceTable > 0x80000000:
                    tables.add((i, desc.KiServiceTable.v(), desc.ServiceLimit.v()))

        print "Finding appropriate address space for tables..."
        tables_with_vm = []
        for idx, table, n in tables:
            found = False
            for p in tasks.pslist(addr_space):
                ## This is the process address space
                ps_ad = p.get_process_address_space()
                ## Is the table accessible from the process AS?
                if ps_ad.is_valid_address(table):
                    tables_with_vm.append((idx, table, n, ps_ad))
                    found = True
                    break
            ## If not we use the kernel address space
            if not found:
                # Any VM is equally bad...
                tables_with_vm.append((idx, table, n, addr_space))

        for idx, table, n, vm in sorted(tables_with_vm, key = itemgetter(0)):
            yield idx, table, n, vm, mods, mod_addrs

    def render_text(self, outfd, data):
        # Print out the entries for each table
        for idx, table, n, vm, mods, mod_addrs in data:
            outfd.write("SSDT[{0}] at {1:x} with {2} entries\n".format(idx, table, n))
            if vm.is_valid_address(table):
                for i in range(n):
                    syscall_addr = obj.Object('unsigned long', table + (i * 4), vm).v()
                    try:
                        syscall_name = xpsp2_syscalls[idx][i]
                    except IndexError:
                        syscall_name = "Unknown"

                    syscall_mod = find_module(mods, mod_addrs, syscall_addr)
                    if syscall_mod:
                        syscall_modname = syscall_mod.BaseDllName
                    else:
                        syscall_modname = "UNKNOWN"

                    outfd.write("  Entry {0:#06x}: {1:#x} ({2}) owned by {3}\n".format(idx * 0x1000 + i,
                                                                       syscall_addr,
                                                                       syscall_name,
                                                                       syscall_modname))
            else:
                outfd.write("  [SSDT not resident at 0x{0:08X} ]\n".format(table))
